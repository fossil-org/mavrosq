import sys


def astral_cli() -> None:
    try:
        path: str = sys.argv[1] if len(sys.argv) > 1 else "main.mav"
        print("Hang tight! We're generating your executable as we speak.")
        print("Did you know Mavro executables are compressed with UPX for minimum size and maximum performance.")
        print("Learn more about UPX: https://upx.github.io/")
        from . import DistBuilder
        builder: DistBuilder = DistBuilder(
            path=path
        )
        builder.buildStdDist()
    except KeyboardInterrupt:
        print("Cancelled build operation")
        return
    print("Build operation successful!")

if __name__ == "__main__":
    astral_cli()