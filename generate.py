import configparser
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus


__all__ = ["main"]


def get_meta(content: str, /) -> dict:
    """Extract a note's metadata."""
    # Use the Python `configparser` for quickness for note metadata
    parser = configparser.ConfigParser(default_section="meta")

    # Get the metadata
    end_tag = "[endmeta]"
    raw_text = content[: content.find(end_tag) + len(end_tag)]
    parser.read_string(raw_text)

    # Pull the metadata out of the base key and append the raw text
    note_meta = parser["meta"]
    note_meta["raw_text"] = raw_text
    parser.clear()
    return note_meta


def get_config() -> dict[str, Path]:
    config = json.loads(Path("config.json").read_text())
    config = {k: Path(v) for k, v in config.items()}
    config["note_path"] = config["output"] / config["note_path"]
    return config


def main():
    # Get the generator config
    config = get_config()

    # Create the output directory
    config["note_path"].mkdir(parents=True, exist_ok=True)

    # Get the templates
    template_index = (config["templates"] / "index.html").read_text()
    template_note = (config["templates"] / "note.html").read_text()

    # Generate each note
    all_notes = []
    for f in config["input"].iterdir():
        # Get the note content
        content = f.read_text()

        # Get the note metadata
        meta = get_meta(content)

        # Remove the raw meta from the text
        content = content.replace(meta["raw_text"], "").strip()

        # Convert the publish date to a datetime object for further processing
        date = datetime.fromisoformat(meta["date"])

        # Fill in all the content
        content = re.sub(r"<!--content-->", content, template_note)
        content = re.sub(r"<!--title-->", meta["title"], content)
        content = re.sub(r"<!--date-->", date.isoformat(), content)

        # Keep a record of the note so we can generate the index when we are done
        note_file = f"{quote_plus(meta['url'])}.html"
        all_notes.append({"title": meta["title"], "date": date, "url": note_file})

        # Write the generated note
        (config["note_path"] / note_file).write_text(content)

    # Sort all of the notes, with the newest on top
    all_notes.sort(key=lambda x: x["date"], reverse=True)

    # Generate the HTML list of all notes for the index
    html = []
    for note in all_notes:
        html.append("<li>")
        html.append('<a href="note/{url}">{title} ({date})</a>'.format_map(note))
        html.append("</li>")
    html = "".join(html)

    # Write the index
    index_content = re.sub("<!--notes-->", html, template_index)
    (config["output"] / "index.html").write_text(index_content)


if __name__ == "__main__":
    main()
