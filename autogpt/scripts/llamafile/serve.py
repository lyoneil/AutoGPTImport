#!/usr/bin/env python3
"""
Use llamafile to serve a (quantized) mistral-7b-instruct-v0.2 model

Usage:
  cd <repo-root>/autogpt
  ./scripts/llamafile/serve.py
"""

import os
import platform
import subprocess
from pathlib import Path
from typing import Optional

import click

LLAMAFILE = Path("mistral-7b-instruct-v0.2.Q5_K_M.llamafile")
LLAMAFILE_URL = f"https://huggingface.co/jartine/Mistral-7B-Instruct-v0.2-llamafile/resolve/main/{LLAMAFILE.name}"  # noqa
LLAMAFILE_EXE = Path("llamafile.exe")
LLAMAFILE_EXE_URL = "https://github.com/Mozilla-Ocho/llamafile/releases/download/0.8.6/llamafile-0.8.6"  # noqa


@click.command()
@click.option(
    "--llamafile",
    type=click.Path(dir_okay=False),
    help=f"Name of the llamafile to serve. Default: {LLAMAFILE.name}",
)
@click.option("--llamafile_url", help="Download URL for the llamafile you want to use")
def main(llamafile: Optional[Path] = None, llamafile_url: Optional[str] = None):
    if not llamafile:
        if not llamafile_url:
            llamafile = LLAMAFILE
        else:
            llamafile = Path(llamafile_url.rsplit("/", 1)[1])
            if llamafile.suffix != ".llamafile":
                click.echo(
                    click.style(
                        "The given URL does not end with '.llamafile' -> "
                        "can't get filename from URL. "
                        "Specify the filename using --llamafile.",
                        fg="red",
                    ),
                    err=True,
                )
                return

    if llamafile == LLAMAFILE and not llamafile_url:
        llamafile_url = LLAMAFILE_URL
    elif llamafile_url != LLAMAFILE_URL:
        if not click.prompt(
            click.style(
                "You seem to have specified a different URL for the default model "
                f"({llamafile.name}). Are you sure this is correct? "
                "If you want to use a different model, also specify --llamafile.",
                fg="yellow",
            ),
            type=bool,
        ):
            return

    # Go to autogpt/scripts/llamafile/
    os.chdir(Path(__file__).resolve().parent)

    if not llamafile.is_file():
        if not llamafile_url:
            click.echo(
                click.style(
                    "Please use --lamafile_url to specify a download URL for "
                    f"'{llamafile.name}'. "
                    "This will only be necessary once, so we can download the model.",
                    fg="red",
                ),
                err=True,
            )
            return

        download_file(llamafile_url, llamafile)

        if platform.system() != "Windows":
            llamafile.chmod(0o755)
            subprocess.run([llamafile, "--version"], check=True)

    if platform.system() != "Windows":
        base_command = [llamafile]
    else:
        # Windows does not allow executables over 4GB, so we have to download a
        # model-less llamafile.exe and extract the model weights (.gguf file)
        # from the downloaded .llamafile.
        if not LLAMAFILE_EXE.is_file():
            download_file(LLAMAFILE_EXE_URL, LLAMAFILE_EXE)
            LLAMAFILE_EXE.chmod(0o755)
            subprocess.run([LLAMAFILE_EXE, "--version"], check=True)

        model_file = llamafile.with_suffix(".gguf")
        if not model_file.is_file():
            import zipfile

            with zipfile.ZipFile(llamafile, "r") as zip_ref:
                gguf_file = next(
                    (file for file in zip_ref.namelist() if file.endswith(".gguf")),
                    None,
                )
                if not gguf_file:
                    raise Exception("No .gguf file found in the zip file.")

                zip_ref.extract(gguf_file)
                Path(gguf_file).rename(model_file)

        base_command = [LLAMAFILE_EXE, "-m", model_file]

    subprocess.run(
        [
            *base_command,
            "--server",
            "--nobrowser",
            "--ctx-size",
            "0",
            "--n-predict",
            "1024",
        ],
        check=True,
    )

    # note: --ctx-size 0 means the prompt context size will be set directly from the
    # underlying model configuration. This may cause slow response times or consume
    # a lot of memory.


def download_file(url: str, to_file: Path) -> None:
    print(f"Downloading {to_file.name}...")
    import urllib.request

    urllib.request.urlretrieve(url, to_file, reporthook=report_download_progress)
    print()


def report_download_progress(chunk_number: int, chunk_size: int, total_size: int):
    if total_size != -1:
        downloaded_size = chunk_number * chunk_size
        percent = min(1, downloaded_size / total_size)
        bar = "#" * int(40 * percent)
        print(
            f"\rDownloading: [{bar:<40}] {percent:.0%}"
            f" - {downloaded_size/1e6:.1f}/{total_size/1e6:.1f} MB",
            end="",
        )


if __name__ == "__main__":
    main()
