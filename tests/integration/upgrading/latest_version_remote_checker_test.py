from protostar.upgrader.latest_version_remote_checker import LatestVersionRemoteChecker


async def test_upgrade_remote_checker():
    upgrade_remote_checker = LatestVersionRemoteChecker()

    result = await upgrade_remote_checker.check()

    assert result.changelog_url.startswith(
        "https://github.com/software-mansion/protostar/releases/tag"
    )
