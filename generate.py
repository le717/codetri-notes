import configparser
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus


__all__ = ["main"]


INPUT = Path("raw")
OUTPUT = Path("generated")
NOTE_OUTPUT = Path("generated") / "note"
TEMPLATE_DIR = Path("templates")


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


def main():
    # Create the output directory
    NOTE_OUTPUT.mkdir(parents=True, exist_ok=True)

    # Get the templates
    template_index = (TEMPLATE_DIR / "index.html").read_text()
    template_note = (TEMPLATE_DIR / "note.html").read_text()

    # Generate each note
    all_notes = []
    for f in INPUT.iterdir():
        # Get the note content
        content = f.read_text()

        # Get the metadata
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
        (NOTE_OUTPUT / note_file).write_text(content)

    # Sort all of the notes, with the newest on top
    all_notes.sort(key=lambda x: x["date"], reverse=True)
    print(all_notes)

    # Generate the HTML list of all notes for the index
    html = []
    for note in all_notes:
        html.append("<li>")
        html.append('<a href="note/{url}">{title} ({date})</a>'.format_map(note))
        html.append("</li>")
    html = "".join(html)
    print(html)

    index_content = re.sub("<!--notes-->", html, template_index)
    (OUTPUT / "index.html").write_text(index_content)


if __name__ == "__main__":
    main()
