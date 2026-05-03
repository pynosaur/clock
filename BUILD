genrule(
    name = "clock_bin",
    srcs = glob(["app/**/*.py", "doc/**/*.yaml"]),
    outs = ["clock"],
    cmd = """
        /opt/homebrew/bin/nuitka \
            --onefile \
            --include-data-dir=doc=doc \
            --onefile-tempdir-spec=/tmp/nuitka-clock \
            --no-progressbar \
            --assume-yes-for-downloads \
            --no-deployment-flag=self-execution \
            --output-dir=$$(dirname $(location clock)) \
            --output-filename=clock \
            $(location app/main.py)
    """,
    local = 1,
    visibility = ["//visibility:public"],
)
