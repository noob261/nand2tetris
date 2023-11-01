import sys
from pathlib import Path
from compilationEngine import CompilationEngine
from jackTokenizer import JackTokenizer


class JackAnalyser:
    def __init__(self) -> None:
        self.infile = Path(sys.argv[1])

    def _initContext(self):
        infile = self.infile
        if infile.is_dir():
            outdir = Path(infile.parents[0]).joinpath(f"My{infile.name}")
        else:
            outdir = Path(infile.parents[1]).joinpath(f"My{infile.parents[0]}")

        if not outdir.exists():
            outdir.mkdir()
        self.outdir = outdir

    def run(self):
        self._initContext()
        infile = self.infile
        if infile.is_dir():  # dir
            for child in infile.iterdir():
                if child.suffix != ".jack":
                    continue
                outfile = self.outdir.joinpath(child.name.replace(".jack", ".xml"))
                self.analyse(child, outfile)
        else:  # single file
            outfile = self.outdir.joinpath(self.infile.name.replace(".jack", ".xml"))
            self.analyse(self.infile, outfile)

    def analyse(self, infile, outfile):
        ce = CompilationEngine(JackTokenizer(infile), outfile)
        ce.compileClass()

if __name__ == "__main__":
    ja = JackAnalyser()
    ja.run()
