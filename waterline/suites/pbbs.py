from waterline import Suite, Benchmark, Workspace, RunConfiguration, Linker
from waterline.utils import run_command
from pathlib import Path
import waterline.utils
import shutil

baseline_flags = [
    "-std=c89",
    "-O1",
    "-Xclang",
    "-disable-llvm-passes",
    "-Xclang",
    "-disable-O0-optnone",
]


class PBBSBenchmark(Benchmark):
    def compile(self, output):
        """
        Compile this benchmark to a certain output directory
        """
        
        bin_path = None
        if self.name == "ch":
            bin_path = "benchmarks/convexHull/bench/hullCheck"
            # bin_path = "benchmarks/convexHull/serialHull/hull"
        elif self.name == "dt":
            bin_path = "benchmarks/delaunayTriangulation/bench/delaunayCheck"
            # bin_path = "benchmarks/delaunayTriangulation/incrementalDelaunay/delaunay"
        elif self.name == "mis":
            bin_path = "benchmarks/maximalIndependentSet/bench/MISCheck"
            # bin_path = ""
        elif self.name == "nbody":
            bin_path = "benchmarks/nBody/bench/nbodyCheck"
        elif self.name == "sf":
            bin_path = "benchmarks/spanningForest/bench/STCheck"

        # if that compiled, copy the binary to the right location
        compiled = self.suite.src / bin_path
        shutil.copy(compiled, output)

    def link(self, object, dest, linker):
        # todo: use linker
        linker.link(
            self.suite.workspace, [object], dest, args=["-fPIC", "-lm", "-fopenmp"]
        )


class PBBS(Suite):
    name = "PBBS"

    def configure(self, enable_openmp=True, suite_class="small"):
        self.enable_openmp = enable_openmp
        self.suite_class = suite_class

        # ["ch", "dt", "mis", "nbody", "sf"]
        self.add_benchmark(PBBSBenchmark, "ch")
        self.add_benchmark(PBBSBenchmark, "dt")
        self.add_benchmark(PBBSBenchmark, "mis")
        self.add_benchmark(PBBSBenchmark, "nbody")
        self.add_benchmark(PBBSBenchmark, "sf")

    def acquire(self):
        self.workspace.shell(
            "git",
            "clone",
            "https://github.com/knagaitsev/pbbsbench.git",
            self.src,
            "--depth",
            "1",
            "--branch",
            "gclang"
        )
        
        self.workspace.shell(
            "git",
            "submodule",
            "update",
            "--init",
            cwd=self.src
        )

        # ignore output of this for now
        try:
            self.workspace.shell(
                "make",
                "-C",
                self.src,
                "-j48"
            )
        except Exception as e:
            print(e)
            pass
