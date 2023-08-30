#! /usr/bin/python3

"""Get-parse song data and show or save"""

import argparse
import os
import music_tag
from lib import parts, colors as color


def parse_args():
    arpa = argparse.ArgumentParser(
        description="Get data from some song",
        epilog="Show song information from MusixMatch",
    )

    arpa.add_argument("-s", "--search", type=str, help="Keyword to search for")
    arpa.add_argument(
        "-u", "--url", type=str, help="URL to use instead of searching one"
    )
    arpa.add_argument("-S", "--show-urls", help="Show all URL found for a keyword", action="store_true")
    plst_grp = arpa.add_argument_group(
        "Playlists",
        "Get the musics from a playlist, put lyrics inside the tags or lrc file",
    )
    plst_grp.add_argument("-p", "--playlist", type=str)
    plst_grp.add_argument(
        "-e", "--embed", help="Put lyrics inside the tags", action="store_true"
    )
    plst_grp.add_argument(
        "-L",
        "--lrc",
        help="Put the lyrics inside a lrc file",
        action="store_true",
    )
    arpa.add_argument(
        "-T",
        "--tries",
        type=int,
        help="Number of tries to get a network response",
        default=5,
    )
    arpa.add_argument(
        "-t", "--timeout", type=int, help="Timeout time in seconds", default=5
    )
    arpa.add_argument(
        "-i", "--index", type=int, help="Index of URL (If using -s)", default=0
    )

    args = arpa.parse_args()

    # Check args as first step
    argsl = [args.search, args.url, args.playlist]
    if all(not arg for arg in argsl):
        arpa.error("one argument of -u/--url, -s/--search, -p/--playlist is required")
    elif sum(1 for item in argsl if item) >= 2:
        arpa.error("only one argument of -u/--url, -s/--search, -p/--playlist allowed")

    return (args, arpa)


def m3u2list(m3u: str = None) -> list[str]:
    """Get a M3U playlist path and return a list with the files path"""
    playlist = []
    with open(m3u, "r", encoding="utf-8") as file:
        for line in file:
            if not line.startswith("#"):
                playlist.append(line.rstrip())
    return playlist


def get_keyword(file: str = None) -> str:
    """Get the song title and artist tag content for a keyword"""
    if file is None:
        raise ValueError("File path cannot be None")
    file = os.path.abspath(file)
    if not os.path.exists(file):
        raise FileNotFoundError(f"File {file} not found")
    music = music_tag.load_file(file)
    return f"{music['title']} - {music['artist']}"


def insert_data(file: str = None, **tags):
    """Insert this data into the audio file tags. Returns the status, when set or not"""
    if file is None:
        raise ValueError("File path cannot be None")
    file = os.path.abspath(file)
    if not os.path.exists(file):
        raise FileNotFoundError(f"File {file} not found")
    try:
        music = music_tag.load_file(file)
        for tag, val in tags.items():
            # if tag in music:
            music[tag] = val
        music.save()
        return True
    # pylint: disable=W0718
    except Exception:
        # Catch any exception and close file
        music.save()
    return False


def main():
    """Main function"""
    args, arpa = parse_args()

    core = parts.Song(
        tries=args.tries,
        timeout=args.timeout,
        cookies=os.environ['MXM_COOKIES'],
        user_agent="Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
    )
    if args.playlist:
        if not any([args.embed, args.lrc]):
            args.lrc = True
        if sum(1 for item in [args.embed, args.lrc] if item) >= 2:
            arpa.error("parameters -e/--embed -L/--lrc not allowed together")
        playlist = m3u2list(args.playlist)
        for audio in playlist:
            # keyword = get_keyword(audio)
            keyword = "Bon Jovi - Runaway"
            print(f"Working on {keyword}...")
            data = core.get_res(keyword=keyword)
            if data is None:
                print(f"Could not get data from {keyword} ({audio})")
                continue
            if args.embed:
                if insert_data(
                    file=audio,
                    title=data["page"]["track"]["name"],
                    artist=data["page"]["track"]["artistName"],
                    album=data["page"]["track"]["albumName"],
                    genre=data["page"]["track"]["primaryGenres"][0]["name"],
                    lyrics=data["page"]["lyrics"]["lyrics"]["body"],
                    comment=keyword,  # Save name and artist into comment if missed
                ):
                    print(f"Data inserted in {audio}, from (may not) '{keyword}'")
                else:
                    print(f"Data not inserted in {audio}, from (may not) '{keyword}'")
            elif args.lrc:
                try:
                    with open(
                        os.path.abspath(f"{os.path.splitext(audio)[0]}.lrc"),
                        "+w",
                        encoding="utf-8",
                    ) as lrc:
                        lrc.write(data["page"]["lyrics"]["lyrics"]["body"])
                    print(f"Lyrics saved into {os.path.splitext(audio)[0]}.lrc file")
                # pylint: disable=W0718,C0103
                except Exception as e:
                    print(f"Lyrics could not be saved saved because {e}")
    elif args.search:
        if args.show_urls:
            urls = core.get_urls(keyword=args.search)
            print("These are all URL we found:\n")
            for index, url in enumerate(urls):
                print(f"    {index} - {color.fg(87)}{url}{color.RESET}")
            return
        data = core.get_res(keyword=args.search, index=args.index)
        if data is None:
            print(f"Could not get data from '{args.search}'")
            return
        if data["page"]["track"]["hasLyrics"] == 1:
            lyrics = f'\n{data["page"]["lyrics"]["lyrics"]["body"]}'
        else:
            lyrics = "This song has no lyrics"
        if data["page"]["lyrics"]["lyrics"]["restricted"] == 1:
            lyrics = "We do not have access to the lyrics"
        print(
            f'Track: "{data["page"]["track"]["name"]}" from "{data["page"]["track"]["artistName"]}"\n'
            f'Album: {data["page"]["track"]["albumName"]}\n'
            f'Genre: {data["page"]["track"]["primaryGenres"][0]["name"]}\n'
            f'Lyrics: {color.from_hex("#ed4c0c")}{lyrics}{color.RESET}\n'
        )
    elif args.url:
        if not core.check_url(url=args.url):
            raise ValueError("Inappropriate URL form")
        data = core.get_data(url=args.url, deserialize=True)
        if data is None:
            print(f"Could not get data from '{args.search}'")
            return
        if data["page"]["track"]["hasLyrics"] == 1:
            lyrics = f'\n{data["page"]["lyrics"]["lyrics"]["body"]}'
        else:
            lyrics = "This song has no lyrics"
        if data["page"]["lyrics"]["lyrics"]["restricted"] == 1:
            lyrics = "We do not have access to the lyrics"
        print(
            f'Track: "{data["page"]["track"]["name"]}" from "{data["page"]["track"]["artistName"]}"\n'
            f'Album: {data["page"]["track"]["albumName"]}\n'
            f'Genre: {data["page"]["track"]["primaryGenres"][0]["name"]}\n'
            f'Lyrics: {color.from_hex("#ed4c0c")}{lyrics}{color.RESET}\n'
        )


if __name__ == "__main__":
    main()
