
        self.demo_timer.stop()
        try:
            self.demo_timer.timeout.disconnect()
        except RuntimeError:
            pass

        file_button = self.findChild(QPushButton, "inspectionFileButton")
        if file_button:
            file_button.clicked.connect(self.select_inspection_files)

        small_buttons = self.findChildren(QPushButton, "inspectionSmallButton")
        for button in small_buttons:
            if "전체 삭제" in button.text():
                button.clicked.connect(self.clear_inspection_files)
            elif button.text() == "전체 선택":
                button.clicked.connect(lambda _checked=False: self.set_all_rule_categories(True))
            elif button.text() == "전체 해제":
                button.clicked.connect(lambda _checked=False: self.set_all_rule_categories(False))

        self._wire_rule_rows()

        try:
            self.start_button.clicked.disconnect()
        except RuntimeError:
            pass
        self.start_button.clicked.connect(self.start_real_inspection)
        self._refresh_file_view()
        self._refresh_rule_summary()

    def _wire_rule_rows(self):
        for row in self.findChildren(QFrame, "inspectionRuleRow"):
            name_label = row.findChild(QLabel, "inspectionRuleName")
            check_label = row.findChild(QLabel, "inspectionCheck")
            view_button = row.findChild(QPushButton, "inspectionViewButton")
            if name_label is None:
                continue
            category = name_label.text()
            row.setProperty("ruleCategory", category)

            if check_label is not None and row.layout() is not None:
                index = row.layout().indexOf(check_label)
                row.layout().removeWidget(check_label)
                check_label.hide()
                toggle = QPushButton("✓")
                toggle.setObjectName("inspectionCheck")
                toggle.setCheckable(True)
                toggle.setChecked(True)
                toggle.setCursor(Qt.PointingHandCursor)
                toggle.setFixedSize(15, 15)
                toggle.clicked.connect(
                    lambda checked, name=category: self.set_rule_category(name, checked)
                )
                row.layout().insertWidget(index, toggle)

            if view_button is not None:
                try:
                    view_button.clicked.disconnect()
                except (RuntimeError, TypeError):
                    pass
                view_button.clicked.connect(
                    lambda _checked=False, name=category: self.open_rule_category_dialog(name)
                )

    def set_rule_category(self, category, selected):
        if selected:
            self.selected_rule_categories.add(category)
        else:
            self.selected_rule_categories.discard(category)
        self._sync_rule_toggle_buttons()
        self._refresh_rule_summary()
