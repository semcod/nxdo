% ── Project Metadata ─────────────────────────────────────
project_metadata('lane', '0.2.19', 'python').

% ── Project Files ────────────────────────────────────────
project_file('app.doql.less', 48, 'less').
project_file('project.sh', 48, 'shell').
project_file('src/lane/__init__.py', 32, 'python').
project_file('src/lane/__main__.py', 7, 'python').
project_file('src/lane/cli.py', 381, 'python').
project_file('src/lane/config.py', 45, 'python').
project_file('src/lane/git_reader.py', 269, 'python').
project_file('src/lane/koru_context.py', 284, 'python').
project_file('src/lane/llm_client.py', 86, 'python').
project_file('src/lane/metrics/__init__.py', 17, 'python').
project_file('src/lane/metrics/complexity.py', 301, 'python').
project_file('src/lane/metrics/coupling.py', 195, 'python').
project_file('src/lane/metrics/hotspots.py', 271, 'python').
project_file('src/lane/models.py', 91, 'python').
project_file('src/lane/output.py', 68, 'python').
project_file('src/lane/planner.py', 59, 'python').
project_file('src/lane/project_analyzer.py', 283, 'python').
project_file('src/lane/providers/__init__.py', 7, 'python').
project_file('src/lane/providers/base.py', 20, 'python').
project_file('src/lane/providers/openai_compat.py', 205, 'python').
project_file('src/lane/ticket_generator.py', 281, 'python').
project_file('tests/test_cli.py', 342, 'python').
project_file('tests/test_config.py', 52, 'python').
project_file('tests/test_git_reader.py', 216, 'python').
project_file('tests/test_llm_client.py', 105, 'python').
project_file('tests/test_metrics.py', 94, 'python').
project_file('tests/test_models.py', 88, 'python').
project_file('tests/test_output.py', 68, 'python').
project_file('tests/test_planner.py', 93, 'python').
project_file('tests/test_project_analyzer.py', 233, 'python').
project_file('tests/test_providers.py', 167, 'python').
project_file('tests/test_ticket_generator.py', 289, 'python').
project_file('tree.sh', 2, 'shell').

% ── Python Functions ─────────────────────────────────────
python_function('src/lane/cli.py', 'cmd_plan', 6, 4, 12).
python_function('src/lane/cli.py', 'cmd_print_context', 3, 2, 10).
python_function('src/lane/cli.py', 'cmd_print_prompt', 3, 1, 10).
python_function('src/lane/cli.py', 'cmd_validate', 1, 2, 8).
python_function('src/lane/cli.py', '_sync_todos_if_requested', 3, 2, 3).
python_function('src/lane/cli.py', '_sync_planfile_if_requested', 3, 3, 3).
python_function('src/lane/cli.py', '_export_yaml_if_requested', 4, 3, 1).
python_function('src/lane/cli.py', '_get_priority_emoji', 1, 1, 1).
python_function('src/lane/cli.py', '_display_tickets', 1, 3, 3).
python_function('src/lane/cli.py', 'cmd_tickets', 10, 3, 16).
python_function('src/lane/cli.py', 'cmd_metrics', 3, 11, 15).
python_function('src/lane/cli.py', 'cmd_auto', 3, 9, 17).
python_function('src/lane/cli.py', 'app_entry', 0, 1, 1).
python_function('src/lane/cli.py', 'main', 1, 4, 15).
python_function('src/lane/config.py', 'get_settings', 0, 2, 1).
python_function('src/lane/git_reader.py', '_run', 2, 3, 2).
python_function('src/lane/git_reader.py', '_is_git_repo', 1, 1, 2).
python_function('src/lane/git_reader.py', '_run_git_command', 3, 2, 1).
python_function('src/lane/git_reader.py', '_get_git_branch', 1, 1, 1).
python_function('src/lane/git_reader.py', '_get_git_remote', 1, 1, 1).
python_function('src/lane/git_reader.py', '_get_git_commits', 2, 1, 2).
python_function('src/lane/git_reader.py', '_count_file_frequencies', 1, 4, 4).
python_function('src/lane/git_reader.py', '_format_file_summary', 1, 2, 2).
python_function('src/lane/git_reader.py', '_get_file_frequency', 2, 1, 3).
python_function('src/lane/git_reader.py', '_get_git_todos', 1, 3, 3).
python_function('src/lane/git_reader.py', '_create_empty_context', 1, 1, 1).
python_function('src/lane/git_reader.py', 'read_git_context', 2, 2, 8).
python_function('src/lane/git_reader.py', '_parse_commit_metadata', 1, 3, 2).
python_function('src/lane/git_reader.py', '_create_commit_info', 2, 1, 2).
python_function('src/lane/git_reader.py', '_finalize_commit', 3, 2, 2).
python_function('src/lane/git_reader.py', '_parse_commits', 1, 5, 5).
python_function('src/lane/git_reader.py', '_filter_git_paths', 1, 3, 1).
python_function('src/lane/git_reader.py', '_should_ignore_git_path', 1, 5, 5).
python_function('src/lane/git_reader.py', '_should_include_todo_line', 1, 2, 3).
python_function('src/lane/koru_context.py', '_load_operations', 0, 3, 2).
python_function('src/lane/koru_context.py', '_load_project_state', 1, 6, 4).
python_function('src/lane/koru_context.py', '_format_operations_for_llm', 1, 7, 6).
python_function('src/lane/koru_context.py', '_format_project_state_for_llm', 1, 7, 4).
python_function('src/lane/koru_context.py', 'build_koru_context', 2, 3, 7).
python_function('src/lane/koru_context.py', 'get_koru_system_prompt_extension', 0, 1, 0).
python_function('src/lane/llm_client.py', 'build_user_prompt', 4, 3, 1).
python_function('src/lane/llm_client.py', 'parse_task_plan_response', 3, 1, 1).
python_function('src/lane/metrics/complexity.py', '_count_lines', 1, 4, 3).
python_function('src/lane/metrics/complexity.py', '_calculate_cyclomatic_complexity', 1, 5, 4).
python_function('src/lane/metrics/complexity.py', '_analyze_imports', 2, 7, 6).
python_function('src/lane/metrics/complexity.py', '_analyze_types', 1, 14, 5).
python_function('src/lane/metrics/complexity.py', '_calculate_fan_in', 2, 12, 12).
python_function('src/lane/metrics/complexity.py', 'collect_file_metrics', 2, 8, 15).
python_function('src/lane/metrics/complexity.py', 'get_high_complexity_files', 3, 4, 0).
python_function('src/lane/metrics/complexity.py', 'get_poorly_typed_files', 2, 4, 0).
python_function('src/lane/metrics/coupling.py', '_get_commits_with_files', 2, 13, 8).
python_function('src/lane/metrics/coupling.py', 'collect_coupling_matrix', 4, 18, 11).
python_function('src/lane/metrics/coupling.py', 'get_coupling_clusters', 2, 10, 8).
python_function('src/lane/metrics/hotspots.py', '_get_file_commits_with_info', 3, 14, 7).
python_function('src/lane/metrics/hotspots.py', '_get_bug_fix_commits', 3, 6, 5).
python_function('src/lane/metrics/hotspots.py', 'identify_bug_hotspots', 4, 16, 15).
python_function('src/lane/metrics/hotspots.py', 'calculate_bus_factor', 3, 14, 7).
python_function('src/lane/metrics/hotspots.py', 'get_critical_bus_factor_files', 2, 7, 9).
python_function('src/lane/output.py', 'render_plan', 2, 4, 8).
python_function('src/lane/output.py', 'render_plan_json', 2, 2, 4).
python_function('src/lane/output.py', 'render_context', 3, 2, 3).
python_function('src/lane/planner.py', 'generate_next_tasks', 5, 5, 8).
python_function('src/lane/project_analyzer.py', '_read_file_safely', 1, 2, 1).
python_function('src/lane/project_analyzer.py', '_truncate_file_content', 1, 2, 1).
python_function('src/lane/project_analyzer.py', '_collect_file_contents', 1, 4, 3).
python_function('src/lane/project_analyzer.py', '_resolve_name_and_description', 3, 3, 5).
python_function('src/lane/project_analyzer.py', 'analyze_project', 1, 1, 5).
python_function('src/lane/project_analyzer.py', '_check_pattern_match', 2, 2, 3).
python_function('src/lane/project_analyzer.py', '_detect_stack', 1, 4, 4).
python_function('src/lane/project_analyzer.py', '_parse_pyproject_tomllib', 2, 4, 3).
python_function('src/lane/project_analyzer.py', '_parse_pyproject_regex', 2, 3, 2).
python_function('src/lane/project_analyzer.py', '_parse_pyproject', 2, 2, 2).
python_function('src/lane/project_analyzer.py', '_parse_package_json', 2, 2, 3).
python_function('src/lane/project_analyzer.py', '_parse_cargo', 2, 3, 2).
python_function('src/lane/project_analyzer.py', '_readme_summary', 1, 4, 3).
python_function('src/lane/project_analyzer.py', '_should_ignore_entry', 1, 4, 4).
python_function('src/lane/project_analyzer.py', '_get_tree_symbol', 2, 4, 0).
python_function('src/lane/project_analyzer.py', '_get_connector', 1, 1, 1).
python_function('src/lane/project_analyzer.py', '_get_extension', 1, 1, 1).
python_function('src/lane/project_analyzer.py', '_get_subtree_lines', 5, 4, 3).
python_function('src/lane/project_analyzer.py', '_build_tree', 4, 6, 12).
python_function('src/lane/providers/openai_compat.py', '_strip_markdown_fences', 1, 3, 4).
python_function('src/lane/providers/openai_compat.py', '_parse_json_response', 1, 3, 4).
python_function('src/lane/providers/openai_compat.py', '_create_task_from_dict', 2, 6, 10).
python_function('src/lane/providers/openai_compat.py', '_parse_tasks_from_data', 1, 2, 4).
python_function('src/lane/providers/openai_compat.py', '_parse_response', 3, 1, 7).
python_function('src/lane/ticket_generator.py', 'task_plan_to_tickets', 1, 3, 2).
python_function('src/lane/ticket_generator.py', '_map_priority', 1, 1, 2).
python_function('src/lane/ticket_generator.py', 'sync_to_todo_md', 2, 1, 6).
python_function('src/lane/ticket_generator.py', '_resolve_todo_path', 1, 3, 1).
python_function('src/lane/ticket_generator.py', '_build_todo_section', 1, 4, 4).
python_function('src/lane/ticket_generator.py', '_sync_todo_section', 2, 2, 6).
python_function('src/lane/ticket_generator.py', '_remove_generated_todo_sections', 1, 1, 5).
python_function('src/lane/ticket_generator.py', '_remove_managed_todo_blocks', 1, 5, 2).
python_function('src/lane/ticket_generator.py', '_remove_legacy_generated_todo_sections', 1, 6, 2).
python_function('src/lane/ticket_generator.py', '_ensure_planfile_installed', 0, 3, 3).
python_function('src/lane/ticket_generator.py', 'sync_to_planfile', 2, 8, 9).
python_function('src/lane/ticket_generator.py', 'export_to_planfile_yaml', 2, 3, 4).

% ── Python Classes ───────────────────────────────────────
python_class('src/lane/config.py', 'LaneSettings').
python_method('LaneSettings', 'api_key', 0, 2, 0).
python_class('src/lane/git_reader.py', 'CommitInfo').
python_method('CommitInfo', '__str__', 0, 2, 2).
python_class('src/lane/git_reader.py', 'GitContext').
python_method('GitContext', 'to_text', 0, 7, 3).
python_class('src/lane/koru_context.py', 'KoruOperation').
python_class('src/lane/koru_context.py', 'KoruProjectState').
python_class('src/lane/koru_context.py', 'KoruContext').
python_class('src/lane/llm_client.py', 'OpenAICompatibleLLMClient').
python_method('OpenAICompatibleLLMClient', '__init__', 4, 3, 2).
python_method('OpenAICompatibleLLMClient', 'generate_task_plan', 4, 1, 2).
python_class('src/lane/metrics/complexity.py', 'FileMetrics').
python_class('src/lane/metrics/coupling.py', 'CouplingMetrics').
python_class('src/lane/metrics/hotspots.py', 'HotspotMetrics').
python_class('src/lane/models.py', 'Priority').
python_class('src/lane/models.py', 'TaskType').
python_class('src/lane/models.py', 'Task').
python_method('Task', '__str__', 0, 7, 2).
python_method('Task', 'to_dict', 0, 2, 1).
python_class('src/lane/models.py', 'TaskPlan').
python_method('TaskPlan', '__str__', 0, 7, 3).
python_method('TaskPlan', 'to_dict', 0, 2, 1).
python_class('src/lane/project_analyzer.py', 'ProjectSnapshot').
python_method('ProjectSnapshot', 'to_text', 0, 5, 2).
python_class('src/lane/providers/base.py', 'LLMProvider').
python_method('LLMProvider', 'generate_plan', 2, 1, 0).
python_class('src/lane/providers/openai_compat.py', 'OpenAICompatProvider').
python_method('OpenAICompatProvider', '__init__', 6, 5, 2).
python_method('OpenAICompatProvider', 'generate_plan', 2, 1, 2).
python_method('OpenAICompatProvider', '_call_api', 1, 5, 10).
python_class('tests/test_cli.py', 'CLITests').
python_method('CLITests', 'test_print_prompt_mode_outputs_prompt', 0, 1, 9).
python_method('CLITests', 'test_print_prompt_includes_extra_context', 0, 1, 8).
python_method('CLITests', 'test_missing_api_key_returns_exit_1', 0, 3, 9).
python_method('CLITests', 'test_print_context_raw_mode', 0, 1, 8).
python_method('CLITests', 'test_json_mode_outputs_json', 0, 3, 10).
python_method('CLITests', 'test_max_commits_override', 0, 1, 7).
python_method('CLITests', 'test_app_entry_exists', 0, 1, 2).
python_method('CLITests', 'test_typer_print_context_command', 0, 1, 7).
python_method('CLITests', 'test_typer_print_context_rich_render', 0, 1, 6).
python_method('CLITests', 'test_plan_command_max_commits_branch', 1, 1, 7).
python_method('CLITests', 'test_cmd_tickets_generates_and_displays', 1, 1, 9).
python_method('CLITests', 'test_cmd_tickets_sync_todo', 1, 1, 9).
python_method('CLITests', 'test_cmd_tickets_export_yaml', 1, 1, 9).
python_method('CLITests', 'test_cmd_tickets_max_commits_branch', 1, 1, 7).
python_method('CLITests', 'test_cmd_tickets_sync_planfile', 1, 1, 9).
python_method('CLITests', 'test_cmd_tickets_value_error', 1, 2, 8).
python_method('CLITests', 'test_typer_print_prompt_command', 0, 1, 7).
python_method('CLITests', 'test_typer_validate_command', 0, 1, 7).
python_method('CLITests', 'test_typer_plan_command_with_mocked_provider', 1, 1, 10).
python_method('CLITests', 'test_typer_plan_command_json_output', 1, 1, 9).
python_method('CLITests', 'test_typer_validate_invalid_json', 0, 2, 8).
python_method('CLITests', 'test_main_module_can_be_imported', 0, 1, 1).
python_method('CLITests', 'test_main_module_has_app_entry', 0, 1, 3).
python_method('CLITests', 'test_cmd_plan_handles_value_error', 1, 1, 9).
python_method('CLITests', 'test_app_entry_calls_app', 1, 1, 3).
python_method('CLITests', 'test_main_json_output', 1, 1, 8).
python_method('CLITests', 'test_main_plain_output', 1, 1, 9).
python_class('tests/test_config.py', 'ConfigTests').
python_method('ConfigTests', 'test_settings_reads_openrouter_key', 0, 1, 3).
python_method('ConfigTests', 'test_settings_prefers_openrouter_over_openai', 0, 1, 3).
python_method('ConfigTests', 'test_settings_falls_back_to_openai_key', 0, 3, 4).
python_method('ConfigTests', 'test_settings_api_key_none_when_no_key_set', 0, 3, 4).
python_method('ConfigTests', 'test_settings_defaults', 0, 1, 2).
python_class('tests/test_git_reader.py', 'GitReaderTests').
python_method('GitReaderTests', 'test_parse_commits_keeps_files_with_each_commit', 0, 1, 4).
python_method('GitReaderTests', 'test_parse_commits_filters_generated_files', 0, 1, 4).
python_method('GitReaderTests', 'test_count_file_frequencies_filters_generated_files', 0, 1, 3).
python_method('GitReaderTests', 'test_parse_commits_empty_log', 0, 1, 2).
python_method('GitReaderTests', 'test_parse_commits_single_commit_no_files', 0, 1, 3).
python_method('GitReaderTests', 'test_read_git_context_non_git_dir', 0, 1, 4).
python_method('GitReaderTests', 'test_git_context_to_text_no_commits', 0, 1, 4).
python_method('GitReaderTests', 'test_git_context_to_text_with_commits_and_files', 0, 1, 5).
python_method('GitReaderTests', 'test_git_context_to_text_with_todos', 0, 1, 4).
python_method('GitReaderTests', 'test_commit_info_str_with_many_files', 0, 2, 4).
python_method('GitReaderTests', 'test_run_returns_empty_on_failure', 1, 1, 5).
python_method('GitReaderTests', 'test_run_returns_empty_on_timeout', 1, 1, 5).
python_method('GitReaderTests', 'test_read_git_context_with_real_git_repo', 2, 1, 5).
python_method('GitReaderTests', 'test_read_git_context_filters_generated_todos', 2, 1, 5).
python_method('GitReaderTests', 'test_read_git_context_with_empty_git_log', 2, 1, 5).
python_class('tests/test_llm_client.py', 'LLMClientTests').
python_method('LLMClientTests', 'test_build_user_prompt_includes_sections', 0, 1, 2).
python_method('LLMClientTests', 'test_build_user_prompt_default_extra_context', 0, 1, 2).
python_method('LLMClientTests', 'test_parse_task_plan_response_strips_fences', 0, 1, 2).
python_method('LLMClientTests', 'test_parse_task_plan_response_invalid_json_raises', 0, 1, 4).
python_method('LLMClientTests', 'test_parse_task_plan_response_non_object_raises', 0, 1, 5).
python_method('LLMClientTests', 'test_parse_task_plan_response_falls_back_to_project_name', 0, 1, 3).
python_method('LLMClientTests', 'test_parse_task_plan_response_invalid_priority_raises', 0, 1, 3).
python_method('LLMClientTests', 'test_openai_llm_client_initialization', 1, 1, 4).
python_method('LLMClientTests', 'test_openai_llm_client_generate_task_plan', 1, 1, 7).
python_class('tests/test_metrics.py', 'MetricsTests').
python_method('MetricsTests', 'test_collect_file_metrics_counts_lines', 0, 1, 7).
python_method('MetricsTests', 'test_collect_file_metrics_calculates_cc', 0, 1, 6).
python_method('MetricsTests', 'test_collect_file_metrics_detects_imports', 0, 1, 7).
python_method('MetricsTests', 'test_collect_file_metrics_ignores_non_matching', 0, 1, 6).
python_method('MetricsTests', 'test_coupling_clusters_group_files', 0, 1, 4).
python_method('MetricsTests', 'test_coupling_clusters_empty_when_low_coupling', 0, 1, 4).
python_method('MetricsTests', 'test_calculate_bus_factor_detects_silos', 0, 1, 0).
python_class('tests/test_models.py', 'TaskModelTests').
python_method('TaskModelTests', 'test_task_string_contains_metadata', 0, 1, 3).
python_method('TaskModelTests', 'test_task_string_fractional_hours', 0, 1, 3).
python_method('TaskModelTests', 'test_task_string_no_hours', 0, 1, 3).
python_method('TaskModelTests', 'test_task_plan_to_dict_serializes_enums', 0, 1, 4).
python_method('TaskModelTests', 'test_task_plan_str_contains_header', 0, 1, 4).
python_method('TaskModelTests', 'test_task_plan_str_shows_dependencies', 0, 1, 4).
python_method('TaskModelTests', 'test_task_plan_str_includes_generated_at_when_set', 0, 1, 3).
python_method('TaskModelTests', 'test_task_pydantic_validation_rejects_bad_priority', 0, 1, 2).
python_class('tests/test_output.py', 'OutputTests').
python_method('OutputTests', 'test_render_plan_displays_summary_and_tasks', 0, 1, 7).
python_method('OutputTests', 'test_render_plan_json_outputs_valid_json', 0, 1, 7).
python_method('OutputTests', 'test_render_context_displays_both_panels', 0, 1, 5).
python_class('tests/test_planner.py', 'PlannerTests').
python_method('PlannerTests', 'test_generate_next_tasks_calls_provider', 3, 1, 8).
python_method('PlannerTests', 'test_generate_next_tasks_uses_default_provider_when_none', 3, 1, 8).
python_class('tests/test_project_analyzer.py', 'ProjectAnalyzerTests').
python_method('ProjectAnalyzerTests', 'test_analyze_project_reads_pyproject_and_readme', 0, 1, 8).
python_method('ProjectAnalyzerTests', 'test_analyze_project_no_manifest', 0, 1, 4).
python_method('ProjectAnalyzerTests', 'test_parse_pyproject_invalid_toml_falls_back_to_regex', 0, 1, 2).
python_method('ProjectAnalyzerTests', 'test_parse_pyproject_valid_toml', 0, 1, 2).
python_method('ProjectAnalyzerTests', 'test_readme_summary_skips_headers', 0, 1, 2).
python_method('ProjectAnalyzerTests', 'test_readme_summary_empty', 0, 1, 2).
python_method('ProjectAnalyzerTests', 'test_analyze_project_readme_only', 0, 1, 5).
python_method('ProjectAnalyzerTests', 'test_parse_package_json', 0, 1, 5).
python_method('ProjectAnalyzerTests', 'test_parse_package_json_invalid', 0, 1, 5).
python_method('ProjectAnalyzerTests', 'test_parse_cargo_toml', 0, 1, 2).
python_method('ProjectAnalyzerTests', 'test_detect_stack_python', 0, 1, 5).
python_method('ProjectAnalyzerTests', 'test_detect_stack_javascript', 0, 1, 5).
python_method('ProjectAnalyzerTests', 'test_detect_stack_rust', 0, 1, 5).
python_method('ProjectAnalyzerTests', 'test_detect_stack_by_extension', 0, 1, 6).
python_method('ProjectAnalyzerTests', 'test_analyze_project_handles_oserror_on_file_read', 0, 2, 6).
python_method('ProjectAnalyzerTests', 'test_analyze_project_truncates_large_files', 0, 1, 5).
python_method('ProjectAnalyzerTests', 'test_analyze_project_uses_package_json_parser', 0, 1, 5).
python_method('ProjectAnalyzerTests', 'test_analyze_project_uses_cargo_parser', 0, 1, 5).
python_method('ProjectAnalyzerTests', 'test_parse_pyproject_tomllib_returns_none_when_tomllib_unavailable', 0, 1, 2).
python_method('ProjectAnalyzerTests', 'test_parse_pyproject_tomllib_returns_none_when_project_not_dict', 0, 1, 2).
python_method('ProjectAnalyzerTests', 'test_build_tree_returns_empty_on_oserror', 0, 1, 3).
python_method('ProjectAnalyzerTests', 'test_build_tree_ignores_generated_artifacts', 0, 1, 7).
python_method('ProjectAnalyzerTests', 'test_should_ignore_entry_filters_generated_names', 0, 1, 3).
python_class('tests/test_providers.py', 'ParseResponseTests').
python_method('ParseResponseTests', 'test_valid_response_parsed', 0, 1, 3).
python_method('ParseResponseTests', 'test_invalid_json_raises', 0, 1, 4).
python_method('ParseResponseTests', 'test_non_object_raises', 0, 1, 5).
python_method('ParseResponseTests', 'test_bad_task_priority_raises', 0, 1, 5).
python_method('ParseResponseTests', 'test_fenced_code_block_stripped', 0, 1, 2).
python_class('tests/test_providers.py', 'OpenAICompatProviderTests').
python_method('OpenAICompatProviderTests', 'test_no_api_key_raises_value_error', 0, 1, 7).
python_method('OpenAICompatProviderTests', 'test_generate_plan_uses_parse_response', 0, 1, 5).
python_method('OpenAICompatProviderTests', 'test_call_api_constructs_correct_payload', 1, 1, 8).
python_method('OpenAICompatProviderTests', 'test_call_api_sets_correct_headers', 1, 1, 5).
python_method('OpenAICompatProviderTests', 'test_call_api_handles_unexpected_response', 1, 1, 7).
python_method('OpenAICompatProviderTests', 'test_call_api_raises_on_http_error', 1, 1, 7).
python_method('OpenAICompatProviderTests', 'test_create_task_from_dict_handles_string_dep', 0, 1, 2).
python_class('tests/test_ticket_generator.py', 'TicketGeneratorTests').
python_method('TicketGeneratorTests', 'test_task_plan_to_tickets', 0, 1, 5).
python_method('TicketGeneratorTests', 'test_map_priority', 0, 1, 2).
python_method('TicketGeneratorTests', 'test_export_to_planfile_yaml', 0, 1, 11).
python_method('TicketGeneratorTests', 'test_sync_to_todo_md_creates_file_with_checkboxes', 0, 1, 11).
python_method('TicketGeneratorTests', 'test_sync_to_todo_md_preserves_existing_content', 0, 1, 8).
python_method('TicketGeneratorTests', 'test_sync_to_todo_md_is_idempotent', 0, 1, 11).
python_method('TicketGeneratorTests', 'test_sync_to_todo_md_removes_legacy_generated_sections', 0, 1, 9).
python_method('TicketGeneratorTests', 'test_resolve_todo_path_prefers_existing', 0, 1, 5).
python_method('TicketGeneratorTests', 'test_build_todo_section_contains_checkboxes', 0, 1, 5).

% ── Dependencies ─────────────────────────────────────────

% ── Makefile Targets ─────────────────────────────────────

% ── Taskfile Tasks ───────────────────────────────────────

% ── Environment Variables ────────────────────────────────
env_variable('OPENROUTER_API_KEY', '*(not set)*', 'Required: OpenRouter API key (https://openrouter.ai/keys)').
env_variable('LLM_MODEL', 'openrouter/qwen/qwen3-coder-next', 'Model (default: openrouter/qwen/qwen3-coder-next)').
env_variable('PFIX_AUTO_APPLY', 'true', 'true = apply fixes without asking').
env_variable('PFIX_AUTO_INSTALL_DEPS', 'true', 'true = auto pip/uv install').
env_variable('PFIX_AUTO_RESTART', 'false', 'true = os.execv restart after fix').
env_variable('PFIX_MAX_RETRIES', '3', '').
env_variable('PFIX_DRY_RUN', 'false', '').
env_variable('PFIX_ENABLED', 'true', '').
env_variable('PFIX_GIT_COMMIT', 'false', 'true = auto-commit fixes').
env_variable('PFIX_GIT_PREFIX', 'pfix:', 'commit message prefix').
env_variable('PFIX_CREATE_BACKUPS', 'false', 'false = disable .pfix_backups/ directory').

% ── TestQL Scenarios ─────────────────────────────────────
testql_scenario('generated-cli-tests.testql.toon.yaml', 'cli').
testql_scenario('generated-from-pytests.testql.toon.yaml', 'integration').

% ── Semantic Facts from SUMD.md ──────────────────────────
sumd_declared_file('app.doql.less', 'doql').
sumd_declared_file('testql-scenarios/generated-cli-tests.testql.toon.yaml', 'testql').
sumd_declared_file('testql-scenarios/generated-from-pytests.testql.toon.yaml', 'testql').
sumd_declared_file('project/map.toon.yaml', 'analysis').
sumd_declared_file('project/logic.pl', 'analysis').
sumd_declared_file('project/calls.toon.yaml', 'analysis').
sumd_interface('cli', 'argparse').
sumd_interface('cli', '').

