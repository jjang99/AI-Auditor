DARK_UI_OVERRIDES = """
/* Sidebar readability */
#sidebarHelpFrame { background-color: #0b131c; border: 1px solid #334155; border-radius: 8px; }
#sidebarHelpTitle { color: #f8fafc; font-size: 12px; font-weight: 700; }
#sidebarGradeText { color: #dbe3ee; font-size: 10px; }
#sidebarGradeA, #sidebarGradeB, #sidebarGradeC, #sidebarGradeD, #sidebarGradeE { font-size: 11px; font-weight: 700; }
#sidebarFooterFrame { background-color: transparent; border-top: 1px solid #243041; }
#sidebarFooterText { color: #cbd5e1; font-size: 10px; }
#projectSeparator { background-color: #273445; border: none; }

/* Projects final readability */
#pageTitle { color:#ffffff; font-size:28px; font-weight:800; }
#pageDescription { color:#d8e2ec; font-size:13px; font-weight:650; }
#projectSearchInput { color:#f4f8fb; background-color:#0d1822; border:1px solid #557187; border-radius:7px; padding:0 14px; font-size:12px; }
#newProjectButton { color:#ffffff; background-color:#1672ef; border:none; border-radius:8px; font-size:12px; font-weight:750; }
#projectCard { background-color:#101d29; border:1px solid #3e586d; border-radius:9px; }
#projectName { color:#ffffff; font-size:15px; font-weight:800; }
#projectDepartment { color:#e5eef6; background-color:#173149; border-radius:4px; padding:2px 5px; font-size:10px; font-weight:650; }
#projectMeta { color:#d7e2eb; font-size:11px; font-weight:650; }
#projectStatus { color:#32dc83; font-size:11px; font-weight:750; }
#projectPendingStatus { color:#d2dce5; font-size:11px; font-weight:700; }
#projectFailedStatus { color:#ff6868; font-size:11px; font-weight:750; }
#projectGradeA, #projectGradeB { color:#22c55e; font-size:21px; font-weight:800; }
#projectGradeC { color:#fbbf24; font-size:21px; font-weight:800; }
#projectGradeD { color:#f97316; font-size:21px; font-weight:800; }
#projectGradeE { color:#ef4444; font-size:21px; font-weight:800; }
#projectGradeNone { color:#94a3b8; font-size:21px; font-weight:800; }
#projectGradeText { color:#f1f5f9; font-size:11px; font-weight:700; }
#projectResultTitle { color:#e1e9f0; font-size:10px; font-weight:700; }
#projectIssueWarning { color:#ff5d68; font-size:15px; font-weight:800; }
#projectIssueGood { color:#2bd46f; font-size:15px; font-weight:800; }
#projectIssueNone { color:#a9b8c5; font-size:15px; font-weight:750; }
#projectResolvedText { color:#f5f8fb; font-size:12px; font-weight:750; }
#projectProgressPercent { color:#eef4f8; font-size:11px; font-weight:650; }
#projectMore { color:#dbe5ed; font-size:18px; font-weight:800; }
#projectTotal { color:#ffffff; font-size:12px; font-weight:750; }

/* Project Detail */
#projectDetailContent { background-color: #09090b; }
#detailBreadcrumb { color: #dbe5f1; font-size: 12px; font-weight: 600; }
#detailSummaryCard, #detailStatCard, #detailBodyCard { background-color: #10161c; border: 1px solid #2b3949; border-radius: 9px; }
#detailProjectName { color: #ffffff; font-size: 25px; font-weight: 700; }
#detailMuted { color: #aeb9c7; font-size: 10px; }
#detailDate { color: #e2e8f0; font-size: 11px; }
#detailLastInspectionLabel { color: #cbd5e1; font-size: 11px; font-weight: 600; }
#detailLastInspectionDate { color: #ffffff; font-size: 12px; font-weight: 700; }
#detailSummaryLabel { color: #cbd5e1; font-size: 11px; font-weight: 600; }
#detailSummaryScore { color: #ffffff; font-size: 34px; font-weight: 700; }
#detailSummaryGrade { color: #22c55e; font-size: 35px; font-weight: 700; }
#detailVerticalDivider { background-color: #2b3949; border: none; }
#detailStatTitle { color: #d5dde7; font-size: 11px; font-weight: 600; }
#detailStatValue, #detailResolvedValue { color: #ffffff; font-size: 22px; font-weight: 700; }
#detailBodyTitle { color: #ffffff; font-size: 13px; font-weight: 700; }
#detailSmallText { color: #d4dde8; font-size: 10px; }
#detailHistoryDate { color: #ffffff; font-size: 11px; font-weight: 700; }
#detailHistoryType { color: #7db7ff; font-size: 10px; font-weight: 500; }
#detailHistoryActive { color: #a855f7; font-size: 12px; }
#detailHistoryInactive { color: #64748b; font-size: 12px; }
#detailIssuesHeader { background-color: transparent; border-bottom: 1px solid #2b3949; }
#detailIssueScroll, #detailIssueContainer { background-color: transparent; border: none; }
#detailIssueListRow { background-color: transparent; border-bottom: 1px solid #2a3542; border-radius:7px; }
#detailIssueListRow:hover { background-color:#172635; border:1px solid #52748d; }
#detailIssueCode { color: #ffffff; font-size: 12px; font-weight: 700; }
#detailIssueDescription { color: #e3eaf2; font-size: 11px; font-weight: 500; }
#detailIssueDetailCode { color: #ffffff; font-size: 15px; font-weight: 700; }
#detailTextLabel { color: #f1f5f9; font-size: 11px; font-weight: 700; }
#detailTextBody { color: #e6edf5; font-size: 11px; }
#detailAIText { color: #f0e5ff; font-size: 11px; }
#detailTagText { color: #e2e8f0; background-color: #17202a; border-radius: 5px; padding: 4px 6px; font-size: 10px; }
#detailMetaRow { background-color: #17202a; border-radius: 5px; }
#detailMetaLabel { color: #aebccc; font-size: 10px; font-weight: 600; }
#detailMetaValue { color: #f1f5f9; font-size: 10px; font-weight: 500; }
#detailBadge_critical { color: #ffe4e6; background-color: #5f171d; border: 1px solid #ef4444; border-radius: 6px; font-size: 10px; font-weight: 700; }
#detailBadge_high { color: #fed7aa; background-color: #4a2412; border: 1px solid #7c2d12; border-radius: 5px; font-size: 9px; font-weight: 700; }
#detailBadge_medium { color: #fde68a; background-color: #453712; border: 1px solid #713f12; border-radius: 5px; font-size: 9px; font-weight: 700; }
#detailBadge_low { color: #bfdbfe; background-color: #172f55; border: 1px solid #1d4ed8; border-radius: 5px; font-size: 9px; font-weight: 700; }
#detailStatusResolved { color: #4ade80; font-size: 9px; font-weight: 700; }
#detailStatusOpen { color: #ff6b6b; font-size: 10px; font-weight: 700; }
#detailActionButton, #detailReInspectButton { font-size: 12px; font-weight: 600; }
"""

LIGHT_UI_OVERRIDES = """
/* Soft Light foundation */
QMainWindow { background-color: #f1f5f9; }
#content, #projectsContent, #projectDetailContent { background-color: #f1f5f9; }
#sidebar { background-color: #f8fafc; border-right: 1px solid #d7e0ea; }
#header { background-color: #f8fafc; border-bottom: 1px solid #d7e0ea; }
/* Projects */
#projectsContent { background-color: #f1f5f9; }
#pageTitle { color: #0f172a; font-size: 28px; font-weight: 700; }
#pageDescription { color: #475569; font-size: 13px; }
#projectSearchInput { color: #0f172a; background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 7px; padding: 0 14px; font-size: 12px; }
#projectSearchInput:focus { border: 1px solid #2563eb; }
#newProjectButton { color: #ffffff; background-color: #2563eb; border: none; border-radius: 8px; font-size: 12px; font-weight: 600; }
#newProjectButton:hover { background-color: #1d4ed8; }
#projectCard { background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 10px; }
#projectCard:hover { background-color: #f8fafc; border: 1px solid #3b82f6; }
#projectName { color: #0f172a; font-size: 15px; font-weight: 700; }
#projectDepartment { color: #334155; background-color: #eaf2ff; border-radius: 4px; padding: 2px 5px; font-size: 10px; }
#projectMeta { color: #475569; font-size: 11px; }
#projectStatus { color: #059669; font-size: 11px; font-weight: 600; }
#projectPendingStatus { color: #475569; font-size: 11px; font-weight: 600; }
#projectFailedStatus { color: #dc2626; font-size: 11px; font-weight: 600; }
#projectGradeA, #projectGradeB { color: #16a34a; font-size: 20px; font-weight: 700; }
#projectGradeC { color: #ca8a04; font-size: 20px; font-weight: 700; }
#projectGradeD { color: #ea580c; font-size: 20px; font-weight: 700; }
#projectGradeE { color: #dc2626; font-size: 20px; font-weight: 700; }
#projectGradeNone { color: #64748b; font-size: 20px; font-weight: 700; }
#projectGradeText { color: #334155; font-size: 11px; font-weight: 600; }
#projectResultTitle { color: #475569; font-size: 10px; font-weight: 600; }
#projectIssueWarning { color: #dc2626; font-size: 15px; font-weight: 700; }
#projectIssueGood { color: #16a34a; font-size: 15px; font-weight: 700; }
#projectIssueNone { color: #64748b; font-size: 15px; font-weight: 700; }
#projectResolvedText { color: #0f172a; font-size: 12px; font-weight: 600; }
#projectProgressPercent { color: #334155; font-size: 11px; }
#projectMore { color: #475569; font-size: 18px; font-weight: 700; }
#projectSeparator { background-color: #d8e0ea; border: none; }
#projectProgressGood, #projectProgressWarning, #projectProgressFailed { background: #e2e8f0; border: none; border-radius: 3px; }
#projectProgressGood::chunk { background: #22c55e; border-radius: 3px; }
#projectProgressWarning::chunk { background: #eab308; border-radius: 3px; }
#projectProgressFailed::chunk { background: #94a3b8; border-radius: 3px; }
#projectTotal { color: #0f172a; font-size: 12px; font-weight: 600; }
#paginationButton { color: #334155; background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 18px; }
#paginationButton:hover { border: 1px solid #2563eb; }
#paginationCurrentButton { color: #ffffff; background-color: #2563eb; border: 1px solid #2563eb; border-radius: 6px; font-size: 12px; font-weight: 700; }

/* Sidebar */
#sidebar { background-color: #f8fafc; border-right: 1px solid #d7e0ea; }
#sidebarHelpFrame { background-color: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; }
#sidebarHelpTitle { color: #0f172a; font-size: 12px; font-weight: 700; }
#sidebarGradeText { color: #334155; font-size: 10px; }
#sidebarGradeA, #sidebarGradeB { color: #16a34a; font-size: 11px; font-weight: 700; }
#sidebarGradeC { color: #ca8a04; font-size: 11px; font-weight: 700; }
#sidebarGradeD { color: #ea580c; font-size: 11px; font-weight: 700; }
#sidebarGradeE { color: #dc2626; font-size: 11px; font-weight: 700; }
#sidebarFooterFrame { background-color: transparent; border-top: 1px solid #dbe3ee; }
#sidebarFooterText { color: #475569; font-size: 10px; }

/* Project Detail */
#projectDetailContent { background-color: #f1f5f9; }
#detailBreadcrumb { color: #334155; font-size: 12px; font-weight: 600; }
#detailSummaryCard, #detailStatCard, #detailBodyCard { background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 9px; }
#detailProjectName { color: #0f172a; font-size: 25px; font-weight: 700; }
#detailMuted { color: #64748b; font-size: 10px; }
#detailDate { color: #334155; font-size: 11px; }
#detailLastInspectionLabel { color: #475569; font-size: 11px; font-weight: 600; }
#detailLastInspectionDate { color: #0f172a; font-size: 12px; font-weight: 700; }
#detailSummaryLabel { color: #475569; font-size: 11px; font-weight: 600; }
#detailSummaryScore { color: #0f172a; font-size: 34px; font-weight: 700; }
#detailSummaryGrade { color: #16a34a; font-size: 35px; font-weight: 700; }
#detailVerticalDivider { background-color: #dbe3ee; border: none; }
#detailStatTitle { color: #475569; font-size: 11px; font-weight: 600; }
#detailStatValue, #detailResolvedValue { color: #0f172a; font-size: 22px; font-weight: 700; }
#detailStatIcon_purple { color: #7c3aed; background-color: #f3e8ff; border-radius: 8px; font-size: 18px; }
#detailStatIcon_blue { color: #2563eb; background-color: #dbeafe; border-radius: 8px; font-size: 18px; }
#detailStatIcon_green { color: #16a34a; background-color: #dcfce7; border-radius: 8px; font-size: 18px; }
#detailSmallText { color: #475569; font-size: 10px; }
QProgressBar#detailProgress, QProgressBar#detailDistribution_critical, QProgressBar#detailDistribution_high, QProgressBar#detailDistribution_medium, QProgressBar#detailDistribution_low { background-color: #e2e8f0; border: none; border-radius: 3px; }
QProgressBar#detailProgress::chunk { background-color: #2563eb; border-radius: 3px; }
QProgressBar#detailDistribution_critical::chunk { background-color: #ef4444; border-radius: 3px; }
QProgressBar#detailDistribution_high::chunk { background-color: #f97316; border-radius: 3px; }
QProgressBar#detailDistribution_medium::chunk { background-color: #eab308; border-radius: 3px; }
QProgressBar#detailDistribution_low::chunk { background-color: #3b82f6; border-radius: 3px; }
#detailBodyTitle { color: #0f172a; font-size: 13px; font-weight: 700; }
#detailLevel_critical { color: #dc2626; } #detailLevel_high { color: #ea580c; } #detailLevel_medium { color: #ca8a04; } #detailLevel_low { color: #2563eb; }
#detailHistoryActive { color: #7c3aed; font-size: 12px; }
#detailHistoryInactive { color: #94a3b8; font-size: 12px; }
#detailHistoryDate { color: #0f172a; font-size: 11px; font-weight: 700; }
#detailHistoryType { color: #2563eb; font-size: 10px; font-weight: 500; }
#detailHistoryButton, #detailSortButton { color: #334155; background-color: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 9px; }
#detailIssuesHeader { background-color: transparent; border-bottom: 1px solid #dbe3ee; }
#detailIssueScroll, #detailIssueContainer { background-color: transparent; border: none; }
#detailIssueListRow { background-color: transparent; border-bottom: 1px solid #e2e8f0; border-radius:7px; }
#detailIssueListRow:hover { background-color:#f1f6fa; border:1px solid #8fa8ba; }
#detailIssueCode { color: #0f172a; font-size: 12px; font-weight: 700; }
#detailIssueDescription { color: #334155; font-size: 11px; font-weight: 500; }
#detailBadge_critical { color: #991b1b; background-color: #fee2e2; border: 1px solid #ef4444; border-radius: 6px; font-size: 10px; font-weight: 700; }
#detailBadge_high { color: #c2410c; background-color: #ffedd5; border: 1px solid #fed7aa; border-radius: 5px; font-size: 9px; font-weight: 700; }
#detailBadge_medium { color: #a16207; background-color: #fef3c7; border: 1px solid #fde68a; border-radius: 5px; font-size: 9px; font-weight: 700; }
#detailBadge_low { color: #1d4ed8; background-color: #dbeafe; border: 1px solid #bfdbfe; border-radius: 5px; font-size: 9px; font-weight: 700; }
#detailStatusResolved { color: #15803d; font-size: 9px; font-weight: 700; }
#detailStatusOpen { color: #b91c1c; font-size: 10px; font-weight: 700; }
#detailIssueDetailCode { color: #0f172a; font-size: 15px; font-weight: 700; }
#detailTextLabel { color: #1e293b; font-size: 11px; font-weight: 700; }
#detailTextBody { color: #334155; font-size: 11px; }
#detailAIBox { background-color: #f5f3ff; border: 1px solid #ddd6fe; border-radius: 6px; }
#detailAIIcon { color: #7c3aed; font-size: 15px; }
#detailAIText { color: #5b21b6; font-size: 11px; }
#detailMetaRow { background-color: #f1f5f9; border-radius: 5px; }
#detailMetaLabel { color: #64748b; font-size: 10px; font-weight: 600; }
#detailMetaValue { color: #0f172a; font-size: 10px; font-weight: 500; }
#detailReInspectButton { color: #ffffff; background-color: #6d28d9; border: 1px solid #7c3aed; border-radius: 6px; font-size: 12px; font-weight: 600; }
#detailReInspectButton:hover { background-color: #5b21b6; }
#detailActionButton { color: #0f172a; background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 12px; font-weight: 600; }
#detailActionButton:hover { border: 1px solid #7c3aed; background-color: #f8fafc; }
"""

# Final light-mode text hierarchy. Kept last in the composed stylesheet so
# page-specific legacy refinements cannot wash these colors out.
LIGHT_TEXT_HIERARCHY_FINAL = r"""
#homeDescription { color:#334155; font-weight:500; }
#homeCardDescription { color:#475569; font-weight:500; }
#whyItemTitle { color:#1e293b; font-weight:700; }
#whyItemBody { color:#475569; font-weight:500; }
#footerText { color:#64748b; }

/* Inspection: selected rows must stay fully readable in light mode.
   Keep the same information hierarchy as dark mode instead of fading
   enabled rule text toward the background. */
#inspectionRuleRow { background:#ffffff; border:1px solid #b9c9dc; }
#inspectionRuleName { color:#0f172a; font-size:10px; font-weight:700; }
#inspectionRuleCount { color:#334155; font-size:9px; font-weight:600; }
#inspectionRuleDescription { color:#475569; font-size:9px; font-weight:500; }
#inspectionViewButton { color:#0f172a; background:#ffffff; border:1px solid #94a3b8; font-weight:600; }
#inspectionBlueNote { color:#2563eb; font-weight:600; }
"""


# Shared visual standard for frozen screens.
# Visual-only: no geometry, margins, fixed sizes, layout or behavior.
DARK_SHARED_VISUAL_FINAL = r"""
/* Administration border language */
#homeCard, #whyFrame, #projectCard,
#detailSummaryCard, #detailStatCard, #detailBodyCard,
#inspectionCard {
    border:1px solid #3e586d;
    border-radius:9px;
}
#projectSearchInput, #detailHistoryButton, #detailSortButton,
#detailActionButton, #inspectionInput, #inspectionUploadBox,
#inspectionFileTable, #inspectionRuleRow, #inspectionSummaryBox,
#inspectionInfoBox, #inspectionProgressInfoBox, #inspectionCompleteInfoBox {
    border-color:#476174;
    border-radius:7px;
}

/* Reports readability hierarchy without changing font geometry */
#pageDescription, #homeDescription { color:#c7d3dd; font-weight:600; }
#homeCardTitle, #whyTitle, #whyItemTitle, #projectName,
#detailBodyTitle, #detailTextLabel, #inspectionSectionTitle,
#inspectionFieldLabel, #inspectionFileCount, #inspectionSummaryTitle {
    color:#f3f7fb; font-weight:800;
}
#homeCardDescription, #whyItemBody, #projectMeta,
#detailMuted, #detailSmallText, #detailIssueDescription,
#detailTextBody, #inspectionDescription, #inspectionUploadText,
#inspectionTableMuted, #inspectionSummaryDetail, #inspectionInfoText {
    color:#c7d3dd; font-weight:600;
}
#inspectionInput { color:#f8fbfd; }

/* Shared hover feedback: clickable controls only */
#inspectionHelpButton:hover, #inspectionSmallButton:hover, #inspectionViewButton:hover {
    background:#27465e; border-color:#6f91a9;
}
#inspectionFileButton:hover, #inspectionStartButton:hover, #inspectionResultButton:hover {
    background:#2c82f3;
}
#inspectionDuplicateButton:hover { color:#fcd34d; }
#inspectionCheck:hover { border:1px solid #93c5fd; }
#inspectionFileDeleteButton:hover { background:#24394b; border-radius:6px; }
#inspectionCancelButton:hover { background:#2a171b; border-color:#ef6b6b; }
"""

LIGHT_SHARED_VISUAL_FINAL = r"""
/* Administration border language */
#homeCard, #whyFrame, #projectCard,
#detailSummaryCard, #detailStatCard, #detailBodyCard,
#inspectionCard {
    border:1px solid #afc1cf;
    border-radius:9px;
}
#projectSearchInput, #detailHistoryButton, #detailSortButton,
#detailActionButton, #inspectionInput, #inspectionUploadBox,
#inspectionFileTable, #inspectionRuleRow, #inspectionSummaryBox,
#inspectionInfoBox, #inspectionProgressInfoBox, #inspectionCompleteInfoBox {
    border-color:#a9bac8;
    border-radius:7px;
}

/* Reports readability hierarchy without changing font geometry */
#pageDescription, #homeDescription { color:#4f687b; font-weight:600; }
#homeCardTitle, #whyTitle, #whyItemTitle, #projectName,
#detailBodyTitle, #detailTextLabel, #inspectionSectionTitle,
#inspectionFieldLabel, #inspectionFileCount, #inspectionSummaryTitle {
    color:#172d3f; font-weight:800;
}
#homeCardDescription, #whyItemBody, #projectMeta,
#detailMuted, #detailSmallText, #detailIssueDescription,
#detailTextBody, #inspectionDescription, #inspectionUploadText,
#inspectionTableMuted, #inspectionSummaryDetail, #inspectionInfoText {
    color:#4f687b; font-weight:600;
}
#inspectionInput { color:#203648; }

/* Shared hover feedback: clickable controls only */
#inspectionHelpButton:hover, #inspectionSmallButton:hover, #inspectionViewButton:hover {
    background:#e0eaf2; border-color:#7f9bad;
}
#inspectionFileButton:hover, #inspectionStartButton:hover, #inspectionResultButton:hover {
    background:#0f63d6;
}
#inspectionDuplicateButton:hover { color:#c2410c; }
#inspectionCheck:hover { border:1px solid #2563eb; }
#inspectionFileDeleteButton:hover { background:#e8eef4; border-radius:6px; }
#inspectionCancelButton:hover { background:#fff1f2; border-color:#dc2626; }
"""


# Projects final visual pass.
# Appended last so both dark/light composed themes keep the frozen Projects hierarchy.
PROJECTS_DARK_FINAL = r"""
#projectsContent { background:#09090b; }
#projectsContent #pageTitle { color:#ffffff; font-size:29px; font-weight:900; }
#projectsContent #pageDescription { color:#f0f4f8; font-size:13px; font-weight:700; }
#projectsContent #projectSearchInput { color:#eef4f8; background:#0b151e; border:1px solid #5b7184; border-radius:7px; padding:0 14px; font-size:12px; }
#projectsContent #newProjectButton { color:#ffffff; background:#0b6cff; border:2px solid #4f94ff; border-radius:9px; font-size:13px; font-weight:900; padding:0 4px; }
#projectsContent #newProjectButton:hover { background:#1d72f2; border-color:#72a7ff; }
#projectsContent #projectCard { background:#101d29; border:1px solid #476174; border-radius:9px; }
#projectsContent #projectCard:hover { background:#122333; border:1px solid #3b82f6; }
#projectsContent #projectName { color:#ffffff; font-size:17px; font-weight:900; }
#projectsContent #projectDepartment { color:#f4f8fb; background:#173149; border:none; border-radius:4px; padding:0 6px; font-size:11px; font-weight:800; }
#projectsContent #projectMeta { color:#f0f4f8; font-size:12px; font-weight:800; }
#projectsContent #projectStatus { color:#35e38a; font-size:12px; font-weight:850; }
#projectsContent #projectPendingStatus { color:#f0f4f8; font-size:12px; font-weight:800; }
#projectsContent #projectFailedStatus { color:#ff626d; font-size:12px; font-weight:850; }
#projectsContent #projectGradeA, #projectGradeB { color:#22d879; font-size:25px; font-weight:900; }
#projectsContent #projectGradeC { color:#ffc52c; font-size:25px; font-weight:900; }
#projectsContent #projectGradeD { color:#ff842c; font-size:25px; font-weight:900; }
#projectsContent #projectGradeE { color:#ff4f5e; font-size:25px; font-weight:900; }
#projectsContent #projectGradeNone { color:#b6c3ce; font-size:25px; font-weight:900; }
#projectsContent #projectGradeText { color:#ffffff; font-size:12px; font-weight:850; }
#projectsContent #projectResultTitle { color:#f4f7fa; font-size:11px; font-weight:800; }
#projectsContent #projectIssueCount { color:#ffffff; font-size:14px; font-weight:900; }
#projectsContent #projectIssueSuffix { color:#f4f7fa; font-size:11px; font-weight:800; padding-bottom:3px; }
#projectsContent #projectIssueWarning { color:#ff5260; font-size:23px; font-weight:900; }
#projectsContent #projectIssueGood { color:#2de17f; font-size:23px; font-weight:900; }
#projectsContent #projectIssueNone { color:#d0d8df; font-size:23px; font-weight:900; }
#projectsContent #projectResolvedText { color:#ffffff; font-size:11px; font-weight:800; }
#projectsContent #projectProgressPercent { color:#ffffff; font-size:12px; font-weight:800; }
#projectsContent #projectTotal { color:#ffffff; font-size:13px; font-weight:850; }
"""

PROJECTS_LIGHT_FINAL = r"""
#projectsContent { background:#f1f5f9; }
#projectsContent #pageTitle { color:#0b1f31; font-size:29px; font-weight:900; }
#projectsContent #pageDescription { color:#29475f; font-size:13px; font-weight:700; }
#projectsContent #projectSearchInput { color:#102b40; background:#ffffff; border:1px solid #8fa6b9; border-radius:7px; padding:0 14px; font-size:12px; }
#projectsContent #newProjectButton { color:#ffffff; background:#075fd7; border:2px solid #034cae; border-radius:9px; font-size:13px; font-weight:900; padding:0 4px; }
#projectsContent #newProjectButton:hover { background:#084fb9; border-color:#063f94; }
#projectsContent #projectCard { background:#ffffff; border:1px solid #7893a9; border-radius:9px; }
#projectsContent #projectCard:hover { background:#f8fbfd; border:1px solid #2563eb; }
#projectsContent #projectName { color:#081c2c; font-size:17px; font-weight:900; }
#projectsContent #projectDepartment { color:#153b58; background:#dceaf6; border:none; border-radius:4px; padding:0 6px; font-size:11px; font-weight:800; }
#projectsContent #projectMeta { color:#15364f; font-size:12px; font-weight:850; }
#projectsContent #projectStatus { color:#067b45; font-size:12px; font-weight:850; }
#projectsContent #projectPendingStatus { color:#334f65; font-size:12px; font-weight:800; }
#projectsContent #projectFailedStatus { color:#bd2432; font-size:12px; font-weight:850; }
#projectsContent #projectGradeA, #projectsContent #projectGradeB { color:#00652f; font-size:27px; font-weight:900; }
#projectsContent #projectGradeC { color:#7a4b00; font-size:27px; font-weight:900; }
#projectsContent #projectGradeD { color:#963400; font-size:27px; font-weight:900; }
#projectsContent #projectGradeE { color:#a80f21; font-size:27px; font-weight:900; }
#projectsContent #projectGradeNone { color:#344f66; font-size:26px; font-weight:900; }
#projectsContent #projectGradeText { color:#071521; font-size:13px; font-weight:900; }
#projectsContent #projectResultTitle { color:#24445d; font-size:11px; font-weight:800; }
#projectsContent #projectIssueCount { color:#081c2c; font-size:14px; font-weight:900; }
#projectsContent #projectIssueSuffix { color:#183247; font-size:11px; font-weight:800; padding-bottom:3px; }
#projectsContent #projectIssueWarning { color:#b8172a; font-size:23px; font-weight:900; }
#projectsContent #projectIssueGood { color:#006b39; font-size:23px; font-weight:900; }
#projectsContent #projectIssueNone { color:#354f64; font-size:23px; font-weight:900; }
#projectsContent #projectResolvedText { color:#071b2b; font-size:11px; font-weight:800; }
#projectsContent #projectProgressPercent { color:#15364f; font-size:12px; font-weight:850; }
#projectsContent #projectTotal { color:#081c2c; font-size:13px; font-weight:850; }
"""
