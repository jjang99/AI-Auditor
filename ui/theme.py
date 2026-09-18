DARK_THEME = """
QMainWindow {
    background-color: #09090b;
}

QWidget {
    color: #e5e7eb;
}

QLabel {
    background-color: transparent;
}

#header {
    background-color: #0d0d0f;
    border-bottom: 1px solid #27272a;
}

#topMenuButton {
    color: #d4d4d8;
    background-color: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 6px 10px;
    font-size: 12px;
    font-weight: 600;
}

#topMenuButton:hover {
    color: #ffffff;
}

#topMenuButton:checked {
    color: #3b82f6;
    border-bottom: 2px solid #3b82f6;
}

#themeButton {
    color: #d4d4d8;
    background-color: transparent;
    border: 1px solid #3f3f46;
    border-radius: 6px;
    font-size: 15px;
}

#themeButton:hover {
    background-color: #27272a;
}

#versionLabel {
    color: #64748b;
    font-size: 11px;
}


/* Home */

#homeTitle {
    color: #ffffff;
    font-size: 54px;
    font-weight: 700;
}

#homeSubtitle {
    color: #3b82f6;
    font-size: 20px;
    font-weight: 700;
}

#homeDescription {
    color: #d4d4d8;
    font-size: 15px;
}

#inspectionStartButton {
    color: #ffffff;
    background-color: #2563eb;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
}

#inspectionStartButton:hover {
    background-color: #1d4ed8;
}

#homeCard {
    background-color: #121214;
    border: 1px solid #27272a;
    border-radius: 10px;
}

#homeCard:hover {
    border: 1px solid #3b82f6;
    background-color: #18181b;
}

#homeCardTitle {
    color: #ffffff;
    font-size: 18px;
    font-weight: 600;
}

#homeCardDescription {
    color: #94a3b8;
    font-size: 13px;
}

#homeCardArrow {
    color: #60a5fa;
    font-size: 18px;
    font-weight: 600;
}

#whyFrame {
    background-color: #121214;
    border: 1px solid #27272a;
    border-radius: 10px;
}

#whyTitle {
    color: #ffffff;
    font-size: 16px;
    font-weight: 600;
}

#whyItemTitle {
    color: #e2e8f0;
    font-size: 13px;
    font-weight: 600;
}

#whyItemBody {
    color: #94a3b8;
    font-size: 11px;
}

#whyDivider {
    background-color: #27272a;
    min-width: 1px;
    max-width: 1px;
}

#footerText {
    color: #71717a;
    font-size: 10px;
}

/* Projects */

#pageTitle {
    color: #ffffff;
    font-size: 28px;
    font-weight: 700;
}

#pageDescription {
    color: #cbd5e1;
    font-size: 13px;
}

#projectSearchInput {
    color: #e5e7eb;
    background-color: #101419;
    border: 1px solid #374151;
    border-radius: 7px;
    padding: 0 14px;
    font-size: 12px;
}

#projectSearchInput:focus {
    border: 1px solid #3b82f6;
}

#newProjectButton {
    color: #ffffff;
    background-color: #0866f5;
    border: none;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 600;
}

#newProjectButton:hover {
    background-color: #1d4ed8;
}

#projectCard {
    background-color: #10161c;
    border: 1px solid #334155;
    border-radius: 10px;
}

#projectCard:hover {
    background-color: #131b23;
    border: 1px solid #3b82f6;
}

#projectFolderIcon {
    color: #3b82f6;
    font-size: 27px;
}

#projectName {
    color: #ffffff;
    font-size: 15px;
    font-weight: 700;
}

#projectDepartment {
    color: #cbd5e1;
    background-color: #16283a;
    border-radius: 4px;
    padding: 2px 5px;
    font-size: 10px;
}

#projectMeta {
    color: #d1d5db;
    font-size: 11px;
}

#projectStatus {
    color: #34d399;
    font-size: 11px;
    font-weight: 600;
}

#projectFailedStatus {
    color: #ef4444;
    font-size: 11px;
    font-weight: 600;
}

#projectFailedScore {
    color: #94a3b8;
    font-size: 22px;
    font-weight: 700;
}

#projectGradeA {
    color: #22c55e;
    font-size: 20px;
    font-weight: 700;
}

#projectGradeB {
    color: #22c55e;
    font-size: 20px;
    font-weight: 700;
}

#projectGradeC {
    color: #fbbf24;
    font-size: 20px;
    font-weight: 700;
}

#projectGradeD {
    color: #f97316;
    font-size: 20px;
    font-weight: 700;
}

#projectGradeE {
    color: #ef4444;
    font-size: 20px;
    font-weight: 700;
}

#projectGradeNone {
    color: #64748b;
    font-size: 20px;
    font-weight: 700;
}

#projectGradeText {
    color: #e5e7eb;
    font-size: 11px;
    font-weight: 600;
}

#projectIssuesText {
    color: #f8fafc;
    font-size: 13px;
    font-weight: 600;
}

#projectResolvedText {
    color: #f8fafc;
    font-size: 12px;
    font-weight: 600;
}

#projectProgress {
    background-color: #263341;
    border: none;
    border-radius: 3px;
}

#projectProgress::chunk {
    background-color: #3b82f6;
    border-radius: 3px;
}

#projectProgressPercent {
    color: #e5e7eb;
    font-size: 11px;
}

#projectMore {
    color: #cbd5e1;
    font-size: 18px;
    font-weight: 700;
}

#projectTotal {
    color: #e5e7eb;
    font-size: 12px;
    font-weight: 600;
}

#paginationButton {
    color: #e5e7eb;
    background-color: #10161c;
    border: 1px solid #334155;
    border-radius: 6px;
    font-size: 18px;
}

#paginationButton:hover {
    border: 1px solid #3b82f6;
}

#paginationCurrentButton {
    color: #ffffff;
    background-color: #0866f5;
    border: 1px solid #2563eb;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 700;
}

/* Sidebar */

#sidebar {
    background-color: #0d1117;
    border-right: 1px solid #1f2937;
}

#sidebarLogo {
    color: #3b82f6;
    font-size: 20px;
    font-weight: 700;
}

#sidebarTitle {
    color: #ffffff;
    font-size: 16px;
    font-weight: 700;
}

#sidebarMenuButton {
    color: #94a3b8;
    background-color: transparent;
    border: none;
    border-radius: 7px;
    padding: 10px 12px;
    text-align: left;
    font-size: 12px;
    font-weight: 600;
}

#sidebarMenuButton:hover {
    color: #ffffff;
    background-color: #151b23;
}

#sidebarMenuButton:checked {
    color: #60a5fa;
    background-color: #162033;
    border-left: 3px solid #3b82f6;
}

#sidebarVersion {
    color: #64748b;
    font-size: 10px;
}

#sidebarHelpFrame {
    background-color: #0b131c;
    border: 1px solid #334155;
    border-radius: 8px;
}

#sidebarHelpTitle {
    color: #ffffff;
    font-size: 11px;
    font-weight: 700;
}

#sidebarGradeText {
    color: #e2e8f0;
    font-size: 9px;
}

#sidebarGradeA {
    color: #22c55e;
    font-size: 10px;
    font-weight: 700;
}

#sidebarGradeB {
    color: #22c55e;
    font-size: 10px;
    font-weight: 700;
}

#sidebarGradeC {
    color: #fbbf24;
    font-size: 10px;
    font-weight: 700;
}

#sidebarGradeD {
    color: #f97316;
    font-size: 10px;
    font-weight: 700;
}

#sidebarGradeE {
    color: #ef4444;
    font-size: 10px;
    font-weight: 700;
}

#sidebarFooterFrame {
    background-color: transparent;
    border-top: 1px solid #1f2937;
}

#sidebarFooterText {
    color: #cbd5e1;
    font-size: 9px;
}

#projectSeparator {
    background: #26313d;
    border: none;
}

#projectResultTitle {
    color: #cbd5e1;
    font-size: 10px;
    font-weight: 600;
}

#projectIssueWarning {
    color: #ef4444;
    font-size: 15px;
    font-weight: 700;
}

#projectIssueGood {
    color: #22c55e;
    font-size: 15px;
    font-weight: 700;
}

#projectIssueNone {
    color: #64748b;
    font-size: 15px;
    font-weight: 700;
}

#projectCancelNote {
    color: #64748b;
    font-size: 8px;
}

#projectProgressGood {
    background: #263341;
    border: none;
    border-radius: 3px;
}

#projectProgressGood::chunk {
    background: #22c55e;
    border-radius: 3px;
}

#projectProgressWarning {
    background: #263341;
    border: none;
    border-radius: 3px;
}

#projectProgressWarning::chunk {
    background: #fbbf24;
    border-radius: 3px;
}

#projectProgressFailed {
    background: #263341;
    border: none;
    border-radius: 3px;
}

#projectProgressFailed::chunk {
    background: #64748b;
    border-radius: 3px;
}

/* =========================================================
   Project Detail
   ========================================================= */

#projectDetailContent {
    background-color: #09090b;
}

#detailBreadcrumb {
    color: #cbd5e1;
    font-size: 11px;
}

#detailSummaryCard,
#detailStatCard,
#detailBodyCard {
    background-color: #10161c;
    border: 1px solid #293747;
    border-radius: 8px;
}

#detailProjectName {
    color: #ffffff;
    font-size: 23px;
    font-weight: 700;
}

#detailMuted {
    color: #94a3b8;
    font-size: 10px;
}

#detailDate {
    color: #dbe3ee;
    font-size: 11px;
}

#detailSummaryLabel {
    color: #cbd5e1;
    font-size: 11px;
}

#detailSummaryScore {
    color: #ffffff;
    font-size: 32px;
    font-weight: 700;
}

#detailSummaryGrade {
    color: #22c55e;
    font-size: 34px;
    font-weight: 700;
}

#detailVerticalDivider {
    background-color: #26313d;
    border: none;
}

#detailStatTitle {
    color: #cbd5e1;
    font-size: 10px;
}

#detailStatValue,
#detailResolvedValue {
    color: #ffffff;
    font-size: 21px;
    font-weight: 700;
}

#detailStatIcon_purple {
    color: #c084fc;
    background-color: #2b1d45;
    border-radius: 8px;
    font-size: 18px;
}

#detailStatIcon_blue {
    color: #60a5fa;
    background-color: #172d4f;
    border-radius: 8px;
    font-size: 18px;
}

#detailStatIcon_green {
    color: #4ade80;
    background-color: #173528;
    border-radius: 8px;
    font-size: 18px;
}

#detailSmallText {
    color: #cbd5e1;
    font-size: 9px;
}

QProgressBar#detailProgress {
    background-color: #263341;
    border: none;
    border-radius: 3px;
}

QProgressBar#detailProgress::chunk {
    background-color: #3b82f6;
    border-radius: 3px;
}

#detailBodyTitle {
    color: #ffffff;
    font-size: 12px;
    font-weight: 700;
}

#detailLevel_critical,
#detailStatusOpen {
    color: #ff4d5a;
}

#detailLevel_high {
    color: #f97316;
}

#detailLevel_medium {
    color: #fbbf24;
}

#detailLevel_low {
    color: #3b82f6;
}

QProgressBar#detailDistribution_critical,
QProgressBar#detailDistribution_high,
QProgressBar#detailDistribution_medium,
QProgressBar#detailDistribution_low {
    background-color: #17202b;
    border: none;
    border-radius: 3px;
}

QProgressBar#detailDistribution_critical::chunk {
    background-color: #ff4d5a;
    border-radius: 3px;
}

QProgressBar#detailDistribution_high::chunk {
    background-color: #f97316;
    border-radius: 3px;
}

QProgressBar#detailDistribution_medium::chunk {
    background-color: #fbbf24;
    border-radius: 3px;
}

QProgressBar#detailDistribution_low::chunk {
    background-color: #3b82f6;
    border-radius: 3px;
}

#detailHistoryActive {
    color: #a855f7;
    font-size: 11px;
}

#detailHistoryInactive {
    color: #475569;
    font-size: 11px;
}

#detailHistoryDate {
    color: #e5e7eb;
    font-size: 9px;
}

#detailHistoryType {
    color: #60a5fa;
    font-size: 8px;
}

#detailHistoryButton,
#detailSortButton {
    color: #cbd5e1;
    background-color: #151c24;
    border: 1px solid #293747;
    border-radius: 6px;
    font-size: 9px;
}

#detailHistoryButton:hover,
#detailSortButton:hover {
    border: 1px solid #7c3aed;
}

#detailIssuesHeader {
    background-color: transparent;
    border-bottom: 1px solid #293747;
}

#detailIssueScroll,
#detailIssueContainer {
    background-color: transparent;
    border: none;
}

#detailIssueListRow {
    background-color: transparent;
    border-bottom: 1px solid #26313d;
}

#detailIssueCode {
    color: #e5e7eb;
    font-size: 10px;
}

#detailIssueDescription {
    color: #cbd5e1;
    font-size: 9px;
}

#detailBadge_critical {
    color: #ff5b61;
    background-color: #3a1d22;
    border: 1px solid #6b2931;
    border-radius: 5px;
    font-size: 8px;
}

#detailBadge_high {
    color: #fb923c;
    background-color: #3a2317;
    border: 1px solid #6b351c;
    border-radius: 5px;
    font-size: 8px;
}

#detailBadge_medium {
    color: #fbbf24;
    background-color: #352d16;
    border: 1px solid #5c4b19;
    border-radius: 5px;
    font-size: 8px;
}

#detailBadge_low {
    color: #60a5fa;
    background-color: #172b4a;
    border: 1px solid #24436c;
    border-radius: 5px;
    font-size: 8px;
}

#detailStatusResolved {
    color: #4ade80;
    font-size: 8px;
}

#detailStatusOpen {
    font-size: 8px;
    font-weight: 700;
}

#detailIssueDetailCode {
    color: #ffffff;
    font-size: 14px;
    font-weight: 700;
}

#detailTextLabel {
    color: #cbd5e1;
    font-size: 9px;
    font-weight: 600;
}

#detailTextBody {
    color: #e2e8f0;
    font-size: 9px;
}

#detailAIBox {
    background-color: #211a35;
    border: 1px solid #49386d;
    border-radius: 6px;
}

#detailAIIcon {
    color: #c084fc;
    font-size: 15px;
}

#detailAIText {
    color: #e9d5ff;
    font-size: 9px;
}

#detailTagText {
    color: #cbd5e1;
    background-color: #151c24;
    border-radius: 5px;
    padding: 4px 6px;
    font-size: 8px;
}

#detailReInspectButton {
    color: #ffffff;
    background-color: #4c2386;
    border: 1px solid #6d3cb0;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
}

#detailReInspectButton:hover {
    background-color: #5b2c99;
}

#detailActionButton {
    color: #e5e7eb;
    background-color: #111b24;
    border: 1px solid #293747;
    border-radius: 6px;
    font-size: 11px;
}

#detailActionButton:hover {
    border: 1px solid #7c3aed;
    background-color: #16212c;
}

/* =========================================================
   Project Detail - readability refinement
   ========================================================= */

#detailBreadcrumb {
    font-size: 10px;
}

#detailProjectName {
    font-size: 24px;
}

#detailSummaryLabel {
    font-size: 11px;
}

#detailStatTitle {
    font-size: 10px;
}

#detailBodyTitle {
    font-size: 12px;
}

#detailIssueCode {
    font-size: 10px;
    font-weight: 600;
}

#detailIssueDescription {
    color: #e2e8f0;
    font-size: 9px;
}

#detailTextLabel {
    color: #cbd5e1;
    font-size: 10px;
    font-weight: 600;
}

#detailTextBody {
    color: #e2e8f0;
    font-size: 9px;
}

#detailAIText {
    color: #e9d5ff;
    font-size: 9px;
}

#detailHistoryDate {
    color: #e5e7eb;
    font-size: 9px;
    font-weight: 600;
}

#detailHistoryType {
    color: #60a5fa;
    font-size: 8px;
}

#detailActionButton,
#detailReInspectButton {
    font-size: 11px;
    font-weight: 600;
}

"""


LIGHT_THEME = """
QMainWindow {
    background-color: #f8fafc;
}

QWidget {
    color: #1e293b;
}

QLabel {
    background-color: transparent;
}

#header {
    background-color: #ffffff;
    border-bottom: 1px solid #e2e8f0;
}

#topMenuButton {
    color: #475569;
    background-color: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 6px 10px;
    font-size: 12px;
    font-weight: 600;
}

#topMenuButton:hover {
    color: #0f172a;
}

#topMenuButton:checked {
    color: #2563eb;
    border-bottom: 2px solid #2563eb;
}

#themeButton {
    color: #475569;
    background-color: transparent;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    font-size: 15px;
}

#themeButton:hover {
    background-color: #f1f5f9;
}

#versionLabel {
    color: #94a3b8;
    font-size: 11px;
}


/* Home - light readability hierarchy */
#homeDescription { color: #334155; }
#homeCardDescription { color: #475569; font-weight: 500; }
#whyItemTitle { color: #1e293b; font-weight: 700; }
#whyItemBody { color: #475569; font-weight: 500; }
#footerText { color: #64748b; }

/* Home */

#homeTitle {
    color: #0f172a;
    font-size: 54px;
    font-weight: 700;
}

#homeSubtitle {
    color: #2563eb;
    font-size: 20px;
    font-weight: 700;
}

#homeDescription {
    color: #475569;
    font-size: 15px;
}

#inspectionStartButton {
    color: #ffffff;
    background-color: #2563eb;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
}

#inspectionStartButton:hover {
    background-color: #1d4ed8;
}

#homeCard {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    min-height: 135px;
}

#homeCard:hover {
    border: 1px solid #3b82f6;
    background-color: #f8fafc;
}

#homeCardTitle {
    color: #0f172a;
    font-size: 18px;
    font-weight: 600;
}

#homeCardDescription {
    color: #64748b;
    font-size: 13px;
}

#homeCardArrow {
    color: #2563eb;
    font-size: 18px;
    font-weight: 600;
}

#whyFrame {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
}

#whyTitle {
    color: #0f172a;
    font-size: 16px;
    font-weight: 600;
}

#whyItemTitle {
    color: #334155;
    font-size: 13px;
    font-weight: 600;
}

#whyItemBody {
    color: #64748b;
    font-size: 11px;
}

#whyDivider {
    background-color: #e2e8f0;
    min-width: 1px;
    max-width: 1px;
}

#footerText {
    color: #94a3b8;
    font-size: 10px;
}

/* Sidebar */

#sidebar {
    background-color: #ffffff;
    border-right: 1px solid #e2e8f0;
}

#sidebarLogo {
    color: #2563eb;
    font-size: 20px;
    font-weight: 700;
}

#sidebarTitle {
    color: #0f172a;
    font-size: 16px;
    font-weight: 700;
}

#sidebarMenuButton {
    color: #64748b;
    background-color: transparent;
    border: none;
    border-radius: 7px;
    padding: 10px 12px;
    text-align: left;
    font-size: 12px;
    font-weight: 600;
}

#sidebarMenuButton:hover {
    color: #0f172a;
    background-color: #f1f5f9;
}

#sidebarMenuButton:checked {
    color: #2563eb;
    background-color: #eff6ff;
    border-left: 3px solid #2563eb;
}

#sidebarVersion {
    color: #94a3b8;
    font-size: 10px;
}

"""