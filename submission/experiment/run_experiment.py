"""Run a declared defect/correction experiment against unmodified AI Auditor code.

The documents are synthetic. This measures seeded-defect detection and the
findings after fixture correction, not human productivity or production accuracy.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

from docx import Document
from openpyxl import Workbook

parser = argparse.ArgumentParser()
parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[2])
parser.add_argument('--out', type=Path, default=Path('temp') / 'measurement-rerun')
parser.add_argument('--port', type=int, default=18081)
args = parser.parse_args()
repo = args.repo.resolve()
out = args.out.resolve()
out.mkdir(parents=True, exist_ok=True)
if (out / 'protocol.json').exists():
    raise SystemExit('This experiment is already declared. Use a new output directory for any rerun.')
sys.path.insert(0, str(repo))
from app.services.local_ai_runtime import LocalAIRuntimeManager
from app.services.inspection_service import InspectionService
from rules.definitions.document_rule_registry import get_implemented_document_rules
from rules.providers.local_ai_provider import LlamaCppAIProvider, LocalAISettings
from rules.providers.local_ai_issue_assessor import LocalAIIssueAssessor
from ui.project_detail_export_patch import _export_report_docx, _export_report_xlsx, _export_report_txt

def now():
    return datetime.now(timezone.utc).isoformat()

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=lambda x: x.value) + '\n', encoding='utf-8')

# Declare the six requirement statements and four mutations before any app run.
requirements = [
    ('REQ-101', '로그인', '구현대상=인증 API; 조건=활성 계정과 일치하는 비밀번호 입력 시; 범위=등록 사용자; 처리=인증 후 30분 유효한 세션을 제공한다; 출력=사용자 식별자와 만료시각; 예외=불일치 시 인증 실패 코드 반환'),
    ('REQ-102', '비밀번호 변경', '구현대상=계정 API; 조건=로그인 상태에서 현재 비밀번호가 일치할 때; 범위=본인 계정; 처리=10자 이상 새 비밀번호를 저장하고 기존 세션을 폐기해야 한다; 출력=변경 완료 코드; 예외=조건 불충족 시 저장하지 않고 오류 코드 반환'),
    ('REQ-103', '회원 조회', '구현대상=회원 API; 조건=관리자 권한으로 회원 식별자 입력 시; 범위=해당 회원 1명; 처리=성명과 가입일을 조회한다; 출력=회원 정보 JSON; 예외=대상 없으면 조회 불가 코드 반환'),
    ('REQ-104', '이메일 변경', '구현대상=계정 API; 조건=로그인 상태에서 본인 인증 완료 시; 범위=본인 계정의 이메일; 처리=중복되지 않은 이메일을 저장해야 한다; 출력=저장 완료 코드; 예외=이미 사용 중이면 변경을 거절한다'),
    ('REQ-105', '회원 탈퇴', '구현대상=계정 API; 조건=로그인 상태에서 비밀번호 재확인 완료 시; 범위=본인 계정; 처리=계정을 탈퇴 상태로 변경하고 세션을 폐기해야 한다; 출력=탈퇴 완료 코드; 예외=본인 확인 실패 시 변경하지 않는다'),
    ('REQ-106', '주문 내역 조회', '구현대상=주문 API; 조건=로그인 상태에서 시작일과 종료일 입력 시; 범위=본인 주문 중 지정 기간; 처리=주문일 역순으로 페이지당 20건을 조회한다; 출력=주문번호와 주문일 및 총액; 예외=시작일이 종료일 이후이면 조회하지 않고 오류 코드 반환'),
]
ground_truth = [
    {'id':'G1', 'rule':'REQ-001', 'defect':'비밀번호 변경 요구사항의 ID 공란', 'before_location':'요구사항정의서.docx / 정의 2', 'correction':'해당 문단에 REQ-102 복원'},
    {'id':'G2', 'rule':'REQ-001', 'defect':'이메일 변경과 회원 탈퇴가 서로 다른 정의인데 REQ-104 중복 사용', 'before_location':'요구사항정의서.docx / 정의 4·5; 추적표.xlsx / 6행 ID', 'correction':'회원 탈퇴의 ID를 REQ-105로 복원하고 추적표 ID도 맞춤'},
    {'id':'G3', 'rule':'REQ-006', 'defect':'주문 내역 조회의 구현대상·조건·범위·출력 미정', 'before_location':'요구사항정의서.docx / 정의 6', 'correction':'위 선언의 REQ-106 구현대상·조건·범위·처리·출력·예외 복원'},
    {'id':'G4', 'rule':'REQ-018', 'defect':'회원 조회의 통합테스트 연결 공란', 'before_location':'추적표.xlsx / 기능추적!G4', 'correction':'TEST-103 복원'},
]

input_files = []
for stage in ('before', 'after'):
    folder = out / stage
    folder.mkdir()
    document = Document()
    document.add_heading('회원·주문 서비스 요구사항 정의서', 0)
    document.add_paragraph('검증용 가상 산출물. 각 문단은 독립된 기능 요구사항 정의이다.')
    for index, (identifier, name, detail) in enumerate(requirements):
        if stage == 'before':
            if index == 1:
                identifier = ''
            elif index == 4:
                identifier = 'REQ-104'
            elif index == 5:
                detail = '구현대상=미정; 조건=미정; 범위=미정; 처리=주문 내역을 조회한다; 출력=미정; 예외=미정'
        document.add_paragraph(f'{identifier} | 요구사항명={name} | {detail}')
    doc_path = folder / '요구사항정의서.docx'
    document.save(doc_path)
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = '기능추적'
    sheet.append(['요구사항ID', '기능명', '유스케이스ID', '화면ID', '프로그램ID', '테이블ID', '통합테스트'])
    for index, (identifier, name, _) in enumerate(requirements):
        number = index + 101
        if stage == 'before' and index == 4:
            identifier = 'REQ-104'
        sheet.append([identifier, name, f'UC-{number}', f'UI-{number}', f'PG-{number}', f'TB-{number}', '' if stage == 'before' and index == 2 else f'TEST-{number}'])
    xlsx_path = folder / '추적표.xlsx'
    workbook.save(xlsx_path)
    input_files.extend([doc_path, xlsx_path])

runtime = LocalAIRuntimeManager(base_dir=repo, port=args.port, startup_timeout=90)
if runtime.is_ready():
    raise SystemExit(f'Port {args.port} is already serving a model; choose an unused port.')
code = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD']).decode().strip()
if subprocess.check_output(['git', '-C', str(repo), 'status', '--porcelain']):
    raise SystemExit('The app worktree must be clean before measurement.')
protocol = {
    'declared_at_utc': now(), 'source_commit': code,
    'purpose':'합성 문서에 주입한 4개 표적 결함의 검출과 수정 후 잔여 지적 비교',
    'human_comparator':False, 'production_documents':False,
    'cases':ground_truth, 'rule_codes':['REQ-001','REQ-006','REQ-018'],
    'runs': ['before', 'after'], 'repetitions_per_stage':1,
    'review_unit':'주입한 표적 결함 단위. 중복 지적은 같은 결함을 중복 정탐으로 세지 않음.',
    'adjudication':'실제 findings를 사전 선언 4개 결함과 대조. 추가 지적은 근거를 검토하고 별도 공개.',
    'after_correction':'생성 스크립트가 4개 지정 결함을 수정함. 앱 자동수정 기능을 뜻하지 않음.',
    'timing_scope':'서버 준비 후 파일 파싱부터 실제 Local AI 검사·위험평가·감리판정·보고서 3형식 저장까지의 클라우드 실행 구간. 사람 작업시간 제외.',
    'manual_time_saved_percent':None,
    'platform':platform.platform(), 'python':platform.python_version(), 'logical_cpu_count':os.cpu_count(),
    'model':{'file':runtime.model_path.name,'sha256':digest(runtime.model_path)},
    'inputs':[{'path':str(p.relative_to(out)), 'sha256':digest(p)} for p in input_files],
    'sampling':{'temperature':0.7,'top_p':0.8,'top_k':20,'min_p':0,'seed':42,'max_tokens':512},
    'disclosure':'단일 합성 사례. 실무 정확도·평균 성능·사람의 작업시간 개선으로 일반화하지 않음.',
}
write_json(out / 'protocol.json', protocol)
write_json(out / 'ground_truth.json', ground_truth)
print('DECLARED', digest(out / 'protocol.json'), flush=True)

calls = []
class RecordedProvider(LlamaCppAIProvider):
    def _complete(self, prompt, response_format=None):
        schema = response_format['json_schema']['name'] if response_format else 'inspection_findings'
        started = time.perf_counter()
        entry = {'sequence':len(calls)+1,'kind':schema,'started_at_utc':now(),'prompt':prompt}
        calls.append(entry)
        print('REQUEST', entry['sequence'], schema, flush=True)
        try:
            answer = super()._complete(prompt, response_format=response_format)
            entry['raw_response'] = answer
            return answer
        except Exception as error:
            entry['error'] = str(error)
            raise
        finally:
            entry['seconds'] = round(time.perf_counter()-started, 6)
            write_json(out / 'local_ai_calls.json', calls)
            print('RESPONSE', entry['sequence'], entry['seconds'], flush=True)

settings = LocalAISettings(base_url=runtime.base_url)
provider = RecordedProvider(settings)
rules = tuple(r for r in get_implemented_document_rules() if r.code in protocol['rule_codes'])
assert len(rules)==3
results = {'protocol_sha256':digest(out / 'protocol.json'),'source_commit':code,'started_at_utc':now(),'stages':{}}
try:
    started = time.perf_counter()
    runtime.start()
    results['server_startup_seconds'] = round(time.perf_counter()-started, 6)
    print('SERVER READY',results['server_startup_seconds'],flush=True)
    for stage in ('before','after'):
        print('STAGE',stage,flush=True)
        started = time.perf_counter()
        service = InspectionService(rules=rules, ai_provider=provider, issue_assessor=LocalAIIssueAssessor(provider))
        paths = [out/stage/'요구사항정의서.docx',out/stage/'추적표.xlsx']
        _, summary = service.run(paths, project_id=None)
        inspection_seconds = time.perf_counter()-started
        issues = []
        for issue in summary.issues:
            row = asdict(issue)
            row.update(title=issue.title,status='미조치')
            assessment=issue.assessment
            if assessment:
                row.update(impact=assessment.impact.value,likelihood=assessment.likelihood.value,
                           impact_reason=assessment.impact_reason,likelihood_reason=assessment.likelihood_reason,
                           severity_reason=assessment.severity_reason)
            issues.append(row)
        report={'summary':[('프로젝트','합성 문서 전후 검증'),('단계',stage),('검사 파일',str(summary.file_count)),('실행 규칙',str(summary.executed_rule_count)),('Issue 후보',str(summary.total_issues))], 'issues':issues}
        _export_report_docx(None,out/stage/'검사보고서.docx',report)
        _export_report_xlsx(None,out/stage/'검사보고서.xlsx',report)
        _export_report_txt(None,out/stage/'검사보고서.txt',report)
        result={'file_count':summary.file_count,'executed_rule_count':summary.executed_rule_count,
                'issue_candidates':summary.total_issues,'inspection_seconds':round(inspection_seconds,6),
                'including_export_seconds':round(time.perf_counter()-started,6),'issues':issues}
        results['stages'][stage]=result
        write_json(out/stage/'actual_results.json',result)
        write_json(out/'results.json',results)
        print('STAGE COMPLETE',stage,summary.total_issues,result['including_export_seconds'],flush=True)
    results['completed_at_utc']=now()
    results['status']='completed'
except Exception as error:
    results['status']='failed'
    results['error']=str(error)
    raise
finally:
    runtime.stop()
    write_json(out/'results.json',results)
    print('RESULT',results.get('status'),flush=True)
