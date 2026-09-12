DARK_UI_OVERRIDES = """
/* Sidebar readability */
#sidebarHelpFrame {
    background-color: #0b131c;
    border: 1px solid #334155;
    border-radius: 8px;
}
#sidebarHelpTitle {
    color: #f8fafc;
    font-size: 12px;
    font-weight: 700;
}
#sidebarGradeText {
    color: #dbe3ee;
    font-size: 10px;
}
#sidebarGradeA,
#sidebarGradeB,
#sidebarGradeC,
#sidebarGradeD,
#sidebarGradeE {
    font-size: 11px;
    font-weight: 700;
}
#sidebarFooterFrame {
    background-color: transparent;
    border-top: 1px solid #243041;
}
#sidebarFooterText {
    color: #cbd5e1;
    font-size: 10px;
}

/* Projects refinement */
#projectSeparator {
    background-color: #273445;
    border: none;
}

/* Project Detail readability */
#projectDetailContent {
    background-color: #09090b;
}
#detailBreadcrumb {
    color: #b8c3d1;
    font-size: 11px;
}
#detailSummaryCard,
#detailStatCard,
#detailBodyCard {
    background-color: #10161c;
    border: 1px solid #2b3949;
    border-radius: 9px;
}
#detailProjectName {
    color: #ffffff;
    font-size: 25px;
    font-weight: 700;
}
#detailMuted {
    color: #9aa8b8;
    font-size: 10px;
}
#detailDate {
    color: #e2e8f0;
    font-size: 11px;
}
#detailSummaryLabel {
    color: #cbd5e1;
    font-size: 11px;
    font-weight: 600;
}
#detailSummaryScore {
    color: #ffffff;
    font-size: 34px;
    font-weight: 700;
}
#detailSummaryGrade {
    color: #22c55e;
    font-size: 35px;
    font-weight: 700;
}
#detailVerticalDivider {
    background-color: #2b3949;
    border: none;
}
#detailStatTitle {
    color: #cbd5e1;
    font-size: 11px;
    font-weight: 600;
}
#detailStatValue,
#detailResolvedValue {
    color: #ffffff;
    font-size: 22px;
    font-weight: 700;
}
#detailBodyTitle {
    color: #ffffff;
    font-size: 13px;
    font-weight: 700;
}
#detailSmallText {
    color: #cbd5e1;
    font-size: 10px;
}
#detailHistoryDate {
    color: #f1f5f9;
    font-size: 10px;
    font-weight: 600;
}
#detailHistoryType {
    color: #60a5fa;
    font-size: 9px;
}
#detailIssueCode {
    color: #f8fafc;
    font-size: 11px;
    font-weight: 600;
}
#detailIssueDescription {
    color: #cbd5e1;
    font-size: 10px;
}
#detailTextLabel {
    color: #cbd5e1;
    font-size: 10px;
    font-weight: 700;
}
#detailTextBody {
    color: #e2e8f0;
    font-size: 10px;
}
#detailAIText {
    color: #eadcff;
    font-size: 10px;
}
#detailTagText {
    color: #d7dee8;
    background-color: #17202a;
    border-radius: 5px;
    padding: 4px 6px;
    font-size: 9px;
}
#detailActionButton,
#detailReInspectButton {
    font-size: 12px;
    font-weight: 600;
}
"""


LIGHT_UI_OVERRIDES = """
/* Projects */
#projectsContent {
    background-color: #f8fafc;
}
#pageTitle {
    color: #0f172a;
    font-size: 28px;
    font-weight: 700;
}
#pageDescription {
    color: #475569;
    font-size: 13px;
}
#projectSearchInput {
    color: #0f172a;
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 7px;
    padding: 0 14px;
    font-size: 12px;
}
#projectSearchInput:focus {
    border: 1px solid #2563eb;
}
#newProjectButton {
    color: #ffffff;
    background-color: #2563eb;
    border: none;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 600;
}
#newProjectButton:hover {
    background-color: #1d4ed8;
}
#projectCard {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
}
#projectCard:hover {
    background-color: #f8fafc;
    border: 1px solid #3b82f6;
}
#projectName {
    color: #0f172a;
    font-size: 15px;
    font-weight: 700;
}
#projectDepartment {
    color: #334155;
    background-color: #eaf2ff;
    border-radius: 4px;
    padding: 2px 5px;
    font-size: 10px;
}
#projectMeta {
    color: #475569;
    font-size: 11px;
}
#projectStatus {
    color: #059669;
    font-size: 11px;
    font-weight: 600;
}
#projectPendingStatus {
    color: #475569;
    font-size: 11px;
    font-weight: 600;
}
#projectFailedStatus {
    color: #dc2626;
    font-size: 11px;
    font-weight: 600;
}
#projectGradeA,
#projectGradeB {
    color: #16a34a;
    font-size: 20px;
    font-weight: 700;
}
#projectGradeC {
    color: #ca8a04;
    font-size: 20px;
    font-weight: 700;
}
#projectGradeD {
    color: #ea580c;
    font-size: 20px;
    font-weight: 700;
}
#projectGradeE {
    color: #dc2626;
    font-size: 20px;
    font-weight: 700;
}
#projectGradeNone {
    color: #64748b;
    font-size: 20px;
    font-weight: 700;
}
#projectGradeText {
    color: #334155;
    font-size: 11px;
    font-weight: 600;
}
#projectResultTitle {
    color: #475569;
    font-size: 10px;
    font-weight: 600;
}
#projectIssueWarning {
    color: #dc2626;
    font-size: 15px;
    font-weight: 700;
}
#projectIssueGood {
    color: #16a34a;
    font-size: 15px;
    font-weight: 700;
}
#projectIssueNone {
    color: #64748b;
    font-size: 15px;
    font-weight: 700;
}
#projectResolvedText {
    color: #0f172a;
    font-size: 12px;
    font-weight: 600;
}
#projectProgressPercent {
    color: #334155;
    font-size: 11px;
}
#projectMore {
    color: #475569;
    font-size: 18px;
    font-weight: 700;
}
#projectSeparator {
    background-color: #d8e0ea;
    border: none;
}
#projectProgressGood,
#projectProgressWarning,
#projectProgressFailed {
    background: #e2e8f0;
    border: none;
    border-radius: 3px;
}
#projectProgressGood::chunk {
    background: #22c55e;
    border-radius: 3px;
}
#projectProgressWarning::chunk {
    background: #eab308;
    border-radius: 3px;
}
#projectProgressFailed::chunk {
    background: #94a3b8;
    border-radius: 3px;
}
#projectTotal {
    color: #0f172a;
    font-size: 12px;
    font-weight: 600;
}
#paginationButton {
    color: #334155;
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    font-size: 18px;
}
#paginationButton:hover {
    border: 1px solid #2563eb;
}
#paginationCurrentButton {
    color: #ffffff;
    background-color: #2563eb;
    border: 1px solid #2563eb;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 700;
}

/* Sidebar - same visual scale as dark */
#sidebar {
    background-color: #ffffff;
    border-right: 1px solid #dbe3ee;
}
#sidebarHelpFrame {
    background-color: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
}
#sidebarHelpTitle {
    color: #0f172a;
    font-size: 12px;
    font-weight: 700;
}
#sidebarGradeText {
    color: #334155;
    font-size: 10px;
}
#sidebarGradeA,
#sidebarGradeB {
    color: #16a34a;
    font-size: 11px;
    font-weight: 700;
}
#sidebarGradeC {
    color: #ca8a04;
    font-size: 11px;
    font-weight: 700;
}
#sidebarGradeD {
    color: #ea580c;
    font-size: 11px;
    font-weight: 700;
}
#sidebarGradeE {
    color: #dc2626;
    font-size: 11px;
    font-weight: 700;
}
#sidebarFooterFrame {
    background-color: transparent;
    border-top: 1px solid #dbe3ee;
}
#sidebarFooterText {
    color: #475569;
    font-size: 10px;
}

/* Project Detail */
#projectDetailContent {
    background-color: #f8fafc;
}
#detailBreadcrumb {
    color: #475569;
    font-size: 11px;
}
#detailSummaryCard,
#detailStatCard,
#detailBodyCard {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 9px;
}
#detailProjectName {
    color: #0f172a;
    font-size: 25px;
    font-weight: 700;
}
#detailMuted {
    color: #64748b;
    font-size: 10px;
}
#detailDate {
    color: #334155;
    font-size: 11px;
}
#detailSummaryLabel {
    color: #475569;
    font-size: 11px;
    font-weight: 600;
}
#detailSummaryScore {
    color: #0f172a;
    font-size: 34px;
    font-weight: 700;
}
#detailSummaryGrade {
    color: #16a34a;
    font-size: 35px;
    font-weight: 700;
}
#detailVerticalDivider {
    background-color: #dbe3ee;
    border: none;
}
#detailStatTitle {
    color: #475569;
    font-size: 11px;
    font-weight: 600;
}
#detailStatValue,
#detailResolvedValue {
    color: #0f172a;
    font-size: 22px;
    font-weight: 700;
}
#detailStatIcon_purple {
    color: #7c3aed;
    background-color: #f3e8ff;
    border-radius: 8px;
    font-size: 18px;
}
#detailStatIcon_blue {
    color: #2563eb;
    background-color: #dbeafe;
    border-radius: 8px;
    font-size: 18px;
}
#detailStatIcon_green {
    color: #16a34a;
    background-color: #dcfce7;
    border-radius: 8px;
    font-size: 18px;
}
#detailSmallText {
    color: #475569;
    font-size: 10px;
}
QProgressBar#detailProgress,
QProgressBar#detailDistribution_critical,
QProgressBar#detailDistribution_high,
QProgressBar#detailDistribution_medium,
QProgressBar#detailDistribution_low {
    background-color: #e2e8f0;
    border: none;
    border-radius: 3px;
}
QProgressBar#detailProgress::chunk {
    background-color: #2563eb;
    border-radius: 3px;
}
QProgressBar#detailDistribution_critical::chunk {
    background-color: #ef4444;
    border-radius: 3px;
}
QProgressBar#detailDistribution_high::chunk {
    background-color: #f97316;
    border-radius: 3px;
}
QProgressBar#detailDistribution_medium::chunk {
    background-color: #eab308;
    border-radius: 3px;
}
QProgressBar#detailDistribution_low::chunk {
    background-color: #3b82f6;
    border-radius: 3px;
}
#detailBodyTitle {
    color: #0f172a;
    font-size: 13px;
    font-weight: 700;
}
#detailLevel_critical,
#detailStatusOpen {
    color: #dc2626;
}
#detailLevel_high {
    color: #ea580c;
}
#detailLevel_medium {
    color: #ca8a04;
}
#detailLevel_low {
    color: #2563eb;
}
#detailHistoryActive {
    color: #7c3aed;
    font-size: 11px;
}
#detailHistoryInactive {
    color: #94a3b8;
    font-size: 11px;
}
#detailHistoryDate {
    color: #0f172a;
    font-size: 10px;
    font-weight: 600;
}
#detailHistoryType {
    color: #2563eb;
    font-size: 9px;
}
#detailHistoryButton,
#detailSortButton {
    color: #334155;
    background-color: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    font-size: 9px;
}
#detailIssuesHeader {
    background-color: transparent;
    border-bottom: 1px solid #dbe3ee;
}
#detailIssueScroll,
#detailIssueContainer {
    background-color: transparent;
    border: none;
}
#detailIssueListRow {
    background-color: transparent;
    border-bottom: 1px solid #e2e8f0;
}
#detailIssueCode {
    color: #0f172a;
    font-size: 11px;
    font-weight: 600;
}
#detailIssueDescription {
    color: #475569;
    font-size: 10px;
}
#detailBadge_critical {
    color: #b91c1c;
    background-color: #fee2e2;
    border: 1px solid #fecaca;
    border-radius: 5px;
    font-size: 8px;
}
#detailBadge_high {
    color: #c2410c;
    background-color: #ffedd5;
    border: 1px solid #fed7aa;
    border-radius: 5px;
    font-size: 8px;
}
#detailBadge_medium {
    color: #a16207;
    background-color: #fef3c7;
    border: 1px solid #fde68a;
    border-radius: 5px;
    font-size: 8px;
}
#detailBadge_low {
    color: #1d4ed8;
    background-color: #dbeafe;
    border: 1px solid #bfdbfe;
    border-radius: 5px;
    font-size: 8px;
}
#detailStatusResolved {
    color: #16a34a;
    font-size: 8px;
}
#detailStatusOpen {
    font-size: 8px;
    font-weight: 700;
}
#detailIssueDetailCode {
    color: #0f172a;
    font-size: 14px;
    font-weight: 700;
}
#detailTextLabel {
    color: #334155;
    font-size: 10px;
    font-weight: 700;
}
#detailTextBody {
    color: #334155;
    font-size: 10px;
}
#detailAIBox {
    background-color: #f5f3ff;
    border: 1px solid #ddd6fe;
    border-radius: 6px;
}
#detailAIIcon {
    color: #7c3aed;
    font-size: 15px;
}
#detailAIText {
    color: #5b21b6;
    font-size: 10px;
}
#detailTagText {
    color: #334155;
    background-color: #f1f5f9;
    border-radius: 5px;
    padding: 4px 6px;
    font-size: 9px;
}
#detailReInspectButton {
    color: #ffffff;
    background-color: #6d28d9;
    border: 1px solid #7c3aed;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
}
#detailReInspectButton:hover {
    background-color: #5b21b6;
}
#detailActionButton {
    color: #0f172a;
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
}
#detailActionButton:hover {
    border: 1px solid #7c3aed;
    background-color: #f8fafc;
}
"""
