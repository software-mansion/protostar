# def test_is_test_file():
#     assert not TestCollector.is_test_file("ex.cairo")
#     assert TestCollector.is_test_file("ex_test.cairo")
#     assert TestCollector.is_test_file("test_ex.cairo")
#     assert not TestCollector.is_test_file("z_test_ex.cairo")


# def test_matching_pattern():
#     match_pattern = re.compile("test_basic.*")
#     collector = TestCollector(
#         target=Path(current_directory, "examples"),
#         include_paths=[str(Path(current_directory, "examples"))],
#     )
#     subjects = collector.collect(match_pattern=match_pattern)
#     test_names = [subject.test_path.name for subject in subjects]
#     assert set(test_names) == set(
#         ["test_basic.cairo", "test_basic_broken.cairo", "test_basic_failure.cairo"]
#     )


# def test_omitting_pattern():
#     should_collect = [
#         "test_basic_broken.cairo",
#         "test_basic_failure.cairo",
#         "test_basic_failure.cairo",
#         "test_basic.cairo",
#         "test_proxy.cairo",
#         "test_cheats.cairo",
#         "test_expect_events.cairo",
#     ]
#     omit_pattern = re.compile(".*invalid.*")
#     collector = TestCollector(
#         target=Path(current_directory, "examples"),
#         include_paths=[str(Path(current_directory, "examples"))],
#     )
#     subjects = collector.collect(omit_pattern=omit_pattern)
#     test_names = [subject.test_path.name for subject in subjects]

#     assert set(test_names) == set(should_collect)

#     assert "test_invalid_syntax.cairo" not in test_names
#     assert "test_no_test_functions.cairo" not in test_names


# def test_breakage_upon_broken_test_file():
#     match_pattern = re.compile("test_invalid_syntax.*")
#     collector = TestCollector(
#         target=Path(current_directory, "examples", "invalid"),
#         include_paths=[str(Path(current_directory, "examples"))],
#     )

#     with pytest.raises(CollectionError):
#         collector.collect(match_pattern=match_pattern)


# def test_collect_specific_file():
#     collector = TestCollector(
#         target=Path(current_directory, "examples", "nested", "test_basic.cairo"),
#         include_paths=[str(Path(current_directory, "examples"))],
#     )
#     subjects = collector.collect()
#     test_names = [subject.test_path.name for subject in subjects]
#     assert test_names == ["test_basic.cairo"]


# def test_collect_specific_function():
#     collector = TestCollector(
#         target=Path(
#             current_directory,
#             "examples",
#             "nested",
#             "test_basic.cairo::test_call_not_deployed",
#         ),
#         include_paths=[str(Path(current_directory, "examples"))],
#     )
#     subjects = collector.collect()
#     test_names = [subject.test_path.name for subject in subjects]
#     assert test_names == ["test_basic.cairo"]
#     assert len(subjects[0].test_functions) == 1
