from .utils import verify_repo_url


def install(url: str):
    if not verify_repo_url(url):
        print("FAIL")
    print("SUCCESS")
