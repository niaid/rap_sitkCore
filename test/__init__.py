def _data_files():
    """
    A dictionary of test data file names to full paths.
    """
    from pathlib import Path

    path_dic = {}
    for p in (Path(__file__).parent / "data").glob("*"):
        if p.is_file():
            path_dic[p.name] = str(p.absolute())
    return path_dic


data_paths = _data_files()
