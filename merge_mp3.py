import subprocess
import sys
import os
""" 
Open a CLI, use one of the following 
python merge_mp3.py <absolute_path_mp3_1> <start_time_1> <end_time_1> <absolute_path_mp3_2> <start_time_2> <end_time_2> <absolute_path_merged_mp3>

or 

python merge_mp3.py <absolute_path_mp3_1> <absolute_path_mp3_2> <start_time_2> <end_time_2> <absolute_path_merged_mp3>

or

python merge_mp3.py <absolute_path_mp3_1> <start_time_1> <end_time_1> <absolute_path_mp3_2> <absolute_path_merged_mp3>

or

python merge_mp3.py <absolute_path_mp3_1> <<absolute_path_mp3_2> <absolute_path_merged_mp3>

"""
def norm(path):
    return os.path.abspath(path).replace("\\", "/")

def build_filter(s1, e1, s2, e2):
    filters = []

    # First input
    if s1 is not None and e1 is not None:
        filters.append(f"[0:a]atrim={s1}:{e1},asetpts=PTS-STARTPTS[a0]")
    else:
        filters.append(f"[0:a]aresample=async=1:first_pts=0[a0]")

    # Second input
    if s2 is not None and e2 is not None:
        filters.append(f"[1:a]atrim={s2}:{e2},asetpts=PTS-STARTPTS[a1]")
    else:
        filters.append(f"[1:a]aresample=async=1:first_pts=0[a1]")

    # Concat
    filters.append("[a0][a1]concat=n=2:v=0:a=1[out]")

    return ";".join(filters)


def merge(file1, file2, output, s1=None, e1=None, s2=None, e2=None):
    file1 = norm(file1)
    file2 = norm(file2)
    output = norm(output)

    filter_complex = build_filter(s1, e1, s2, e2)

    cmd = [
        "ffmpeg",
        "-i", file1,
        "-i", file2,
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-acodec", "libmp3lame",
        "-ab", "192k",
        output
    ]

    print("\nRunning:")
    print(" ".join(cmd), "\n")

    subprocess.run(cmd, check=True)
    print(f"✅ Output created: {output}")


if __name__ == "__main__":
    args = sys.argv[1:]

    try:
        if len(args) == 7:
            # full trim both
            f1, s1, e1, f2, s2, e2, out = args
            merge(f1, f2, out, s1, e1, s2, e2)

        elif len(args) == 5:
            # either trim first OR trim second
            f1, a, b, f2, out = args

            # detect if a,b are times or file
            try:
                float(a); float(b)
                # trim first file
                merge(f1, f2, out, a, b, None, None)
            except:
                # trim second file
                f1, f2, s2, e2, out = args
                merge(f1, f2, out, None, None, s2, e2)

        elif len(args) == 3:
            # no trimming
            f1, f2, out = args
            merge(f1, f2, out)

        else:
            raise ValueError

    except Exception:
        print("\nUsage:")
        print("1) python merge_mp3.py f1 s1 e1 f2 s2 e2 out")
        print("2) python merge_mp3.py f1 f2 s2 e2 out")
        print("3) python merge_mp3.py f1 s1 e1 f2 out")
        print("4) python merge_mp3.py f1 f2 out\n")
        sys.exit(1)