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


tests = [
    ["integerSort/parallelRadixSort",True,0],
    ["integerSort/serialRadixSort",False,0],

    ["comparisonSort/sampleSort",True,0],
    ["comparisonSort/quickSort",True,1],
    ["comparisonSort/mergeSort",True,1],
    ["comparisonSort/stableSampleSort",True,1],
    ["comparisonSort/serialSort",False,0],
    ["comparisonSort/ips4o",True,1],

    ["removeDuplicates/serial_hash", False,0],
    ["removeDuplicates/serial_sort", False,1],
    ["removeDuplicates/parlayhash", True,0],

    ["histogram/sequential",False,0],
    ["histogram/parallel",True,0],
    
    ["wordCounts/histogram",True,0],
    # ["wordCounts/histogramStar",True],
    ["wordCounts/serial",False,0],

    ["invertedIndex/sequential", False,0],
    ["invertedIndex/parallel", True,0],
    
    ["suffixArray/parallelKS",True,1],
    ["suffixArray/parallelRange",True,0],
    ["suffixArray/serialDivsufsort",False,0],

    ["longestRepeatedSubstring/doubling",True,0],

    ["classify/decisionTree", True,0],

    # ["minSpanningForest/parallelKruskal",True],
    ["minSpanningForest/parallelFilterKruskal",True,0],
    ["minSpanningForest/serialMST",False,0],

    ["spanningForest/incrementalST",True,1],
    ["spanningForest/ndST",True,0],
    ["spanningForest/serialST",False,0],

    ["breadthFirstSearch/simpleBFS",True,1],
    ["breadthFirstSearch/backForwardBFS",True,0],
    ["breadthFirstSearch/deterministicBFS",True,1],
    ["breadthFirstSearch/serialBFS",False,0],

    ["maximalMatching/serialMatching",False,0],
    ["maximalMatching/incrementalMatching",True,0],

    ["maximalIndependentSet/incrementalMIS",True,0],
    ["maximalIndependentSet/ndMIS",True,1],
    ["maximalIndependentSet/serialMIS",False,0],

    ["nearestNeighbors/octTree",True,0],

    ["rayCast/kdTree",True,0],

    ["convexHull/quickHull",True,0],
    ["convexHull/serialHull",False,0],

    ["delaunayTriangulation/incrementalDelaunay",True,0],

    ["delaunayRefine/incrementalRefine",True,0],
    
    ["rangeQuery2d/parallelPlaneSweep",True,0],
    ["rangeQuery2d/serial",False,0],

    ["nBody/parallelCK",True,0],
]

class PBBSBenchmark(Benchmark):
    def compile(self, output):
        """
        Compile this benchmark to a certain output directory
        """
        
        bin_path = None
        if self.suite.enable_openmp:
            if self.name == "ch":
                bin_path = "benchmarks/convexHull/quickHull/hull"
            elif self.name == "dt":
                bin_path = "benchmarks/delaunayTriangulation/incrementalDelaunay/delaunay"
            elif self.name == "mis":
                bin_path = "benchmarks/maximalIndependentSet/incrementalMIS/MIS"
            elif self.name == "nbody":
                bin_path = "benchmarks/nBody/parallelCK/nbody"
            elif self.name == "sf":
                bin_path = "benchmarks/spanningForest/incrementalST/ST"
        else:
            if self.name == "ch":
                bin_path = "benchmarks/convexHull/serialHull/hull"
            elif self.name == "dt":
                # not actually serial!
                bin_path = "benchmarks/delaunayTriangulation/incrementalDelaunay/delaunay"
            elif self.name == "mis":
                bin_path = "benchmarks/maximalIndependentSet/serialMIS/MIS"
            elif self.name == "nbody":
                # not actually serial!
                bin_path = "benchmarks/nBody/parallelCK/nbody"
            elif self.name == "sf":
                bin_path = "benchmarks/spanningForest/serialST/ST"
        # if self.name == "ch":
        #     bin_path = "benchmarks/convexHull/bench/hullCheck"
        # elif self.name == "dt":
        #     bin_path = "benchmarks/delaunayTriangulation/bench/delaunayCheck"
        # elif self.name == "mis":
        #     bin_path = "benchmarks/maximalIndependentSet/bench/MISCheck"
        # elif self.name == "nbody":
        #     bin_path = "benchmarks/nBody/bench/nbodyCheck"
        # elif self.name == "sf":
        #     bin_path = "benchmarks/spanningForest/bench/STCheck"

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
