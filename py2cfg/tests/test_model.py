#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Working!
"""

import collections
import unittest
import ast
import sys
import os
import functools
import textwrap

# Relative and absolute version of the same thing for interpreter tolerance
sys.path.append("..")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from py2cfg.model import *
from py2cfg.builder import CFGBuilder


class TestBlock(unittest.TestCase):
    def test_instanciation(self):
        block = Block(1)
        self.assertEqual(block.id, 1)
        self.assertEqual(block.statements, [])
        self.assertEqual(block.func_calls, [])
        self.assertEqual(block.predecessors, [])
        self.assertEqual(block.exits, [])

    def test_str_representation(self):
        block = Block(1)
        self.assertEqual(str(block), "empty block:1")
        tree = ast.parse("a = 1")
        block.statements.append(tree.body[0])
        self.assertEqual(str(block), "block:1@1")

    def test_repr(self):
        block = Block(1)
        self.assertEqual(repr(block), "empty block:1 with 0 exits")
        tree = ast.parse("a = 1")
        block.statements.append(tree.body[0])
        self.assertEqual(
            repr(block),
            f"block:1@1 with 0 exits, body=[{ast.dump(tree.body[0])}]",
        )

    def test_at(self):
        block = Block(1)
        self.assertEqual(block.at(), -1)
        tree = ast.parse("a = 1")
        block.statements.append(tree.body[0])
        self.assertEqual(block.at(), 1)

    def test_is_empty(self):
        block = Block(1)
        self.assertTrue(block.is_empty())
        tree = ast.parse("a = 1")
        block.statements.append(tree.body[0])
        self.assertFalse(block.is_empty())

    def test_get_source(self):
        block = Block(1)
        self.assertEqual(block.get_source(), "")
        tree = ast.parse("a = 1")
        block.statements.append(tree.body[0])
        self.assertEqual(block.get_source(), "a = 1\n")

    def test_get_calls(self):
        block = Block(1)
        self.assertEqual(block.get_calls(), "")
        block.func_calls.append("fun")
        self.assertEqual(block.get_calls(), "fun\n")


class TestLink(unittest.TestCase):
    def test_instanciation(self):
        block1 = Block(1)
        block2 = Block(2)
        with self.assertRaises(AssertionError):
            Link(2, block2)  # Source of a link must be a block.
            Link(block1, 2)  # Target of a link must be a block.

        condition = ast.parse("a == 1").body[0]
        link = Link(block1, block2, condition)
        self.assertEqual(link.source, block1)
        self.assertEqual(link.target, block2)
        self.assertEqual(link.exitcase, condition)

    def test_str_representation(self):
        block1 = Block(1)
        block2 = Block(2)
        link = Link(block1, block2)
        self.assertEqual(str(link), "link from empty block:1 to empty block:2")

    def test_repr(self):
        block1 = Block(1)
        block2 = Block(2)
        condition = ast.parse("a == 1").body[0]
        link = Link(block1, block2, condition)
        self.assertEqual(
            repr(link),
            "link from empty block:1 to empty block:2, with exitcase {}".format(
                ast.dump(condition)
            ),
        )

    def test_get_exitcase(self):
        block1 = Block(1)
        block2 = Block(2)
        condition = ast.parse("a == 1").body[0]
        link = Link(block1, block2, condition)
        self.assertEqual(link.get_exitcase(), "a == 1\n")


def source(src, attr="entryblock", build_src=[]):
    src = textwrap.dedent(src)

    def _wrapper(func):
        build_src.append((func.__name__, src))

        @functools.wraps(func)
        def test_wrapper(self):
            cfg = CFGBuilder(
                treebuf=collections.defaultdict(collections.deque)
            ).build_from_src("test", src)
            setattr(self, attr, cfg.entryblock)
            self.cfg = cfg
            return func(self)

        return test_wrapper

    return _wrapper


class TestCFG(unittest.TestCase):
    def test_instanciation(self):
        with self.assertRaises(AssertionError):
            CFG(2, False)  # Name of a CFG must be a string.
            CFG("cfg", 2)  # Async argument must be a boolean.

        cfg = CFG("cfg", False)
        self.assertEqual(cfg.name, "cfg")
        self.assertFalse(cfg.asynchr)
        self.assertEqual(cfg.entryblock, None)
        self.assertEqual(cfg.finalblocks, [])
        self.assertEqual(cfg.functioncfgs, {})

    def test_str_representation(self):
        cfg = CFG("cfg", False)
        self.assertEqual(str(cfg), "CFG for cfg")

    def test_iter(self):
        src = textwrap.dedent(
            """
            def fib():
                a, b = 0, 1
                while True:
                    yield a
                    a, b = b, a + b
        """
        )
        cfg = CFGBuilder().build_from_src("fib", src)
        expected_block_sources = [
            "def fib():...\n",
            "a, b = 0, 1\n",
            "while True:\n",
            "yield a\n",
            "a, b = b, a + b\n",
        ]
        for actual_block, expected_src in zip(cfg, expected_block_sources):
            self.assertEqual(actual_block.get_source(), expected_src)

    @source(
        """
        def min(x, y):
            if x < y:
                return x
            elif x > y:
                return y
            else:
                return x
    """
    )
    def test_find_path(self):
        cfg: CFG = self.cfg.functioncfgs["min"]
        path = cfg.find_path(cfg.finalblocks[0])
        self.assertEqual(len(path), 2)
        l0_ops = path[0].exitcase.ops[0]
        l1_ops = path[1].exitcase.ops[0]
        self.assertTrue(isinstance(l0_ops, ast.GtE))
        self.assertTrue(isinstance(l1_ops, ast.LtE))


class TestCalls(unittest.TestCase):
    @source("int(input(str(10)))")
    def test_stack_order(self):
        self.assertEqual(len(self.entryblock.func_blocks), 1)
        # int()
        func_block = self.entryblock.func_blocks[0]
        self.assertEqual(len(func_block.args), 1)

        # input()
        func_block = func_block.args[0]
        self.assertEqual(len(func_block.args), 1)

        # str()
        func_block = func_block.args[0]
        self.assertEqual(len(func_block.args), 0)

    @source("int(input(str(10)))\n" "int(input(str(20)))\n")
    def test_multiple_func_calls(self):
        self.assertEqual(len(self.entryblock.func_blocks), 2)
        for func_block in self.entryblock.func_blocks:
            # int()
            self.assertEqual(len(func_block.args), 1)
            # input()
            func_block = func_block.args[0]
            self.assertEqual(len(func_block.args), 1)
            # str()
            func_block = func_block.args[0]
            self.assertEqual(len(func_block.args), 0)

    @source("int(add(int(), input()))")
    def test_multiple_calls(self):
        func_block = self.entryblock.func_blocks[0]
        self.assertEqual(len(func_block.args), 1)
        func_block = func_block.args[0]
        self.assertEqual(len(func_block.args), 2)

        self.assertEqual("int", func_block.args[0].name)
        self.assertEqual("input", func_block.args[1].name)


class Test_Try(unittest.TestCase):
    sources = []  # type: ignore

    @classmethod
    def tearDownClass(cls) -> None:
        # Generate graphs for all test case sources
        aggregate = ""
        for name, src in cls.sources:
            aggregate += (
                f"def {name}():"
                + "".join(
                    "    " + line for line in src.splitlines(keepends=True)
                )
                + "\n"
            )

        cfg = CFGBuilder().build_from_src("", aggregate)
        cfg.build_visual("_Test_Try", format="svg", calls=True, show=False)

    def run_trace(self, dest, block=None, trace_num=-1):
        if block is None:
            block = self.entryblock
        visited = set()
        while True:
            if block in visited:
                if issubclass(block.type(), ast.Return) or issubclass(
                    block.type(), ast.Raise
                ):
                    break

            visited.add(block)

            for statement in block.statements:
                if isinstance(statement, ast.Assign):
                    if isinstance(statement.value, ast.UnaryOp):
                        # trace = -1
                        self.assertEqual(trace_num + 1, -1)
                    else:
                        self.assertEqual(statement.value.value, trace_num + 1)
                    trace_num += 1

                elif isinstance(statement, ast.Return):
                    self.assertEqual(statement.value.value, trace_num + 1)
                    trace_num += 1

            if not block.exits:
                break

            block = block.exits[0].target
        self.assertEqual(dest, trace_num)

    def try_block(self):
        block = self.entryblock
        while True:
            if isinstance(block, TryBlock):
                return block
            if not block.exits:
                raise ValueError("Try block not found")
            block = block.exits[0].target

    def run_except_trace(self, dest):
        try_block = self.try_block()
        if try_block.except_blocks:
            for except_block in try_block.except_blocks.values():
                self.run_trace(
                    dest,
                    block=except_block,
                    trace_num=except_block.statements[0].value.value - 1,
                )

    @source(
        """
        trace = 0
        try:
            trace = 1
        finally:
            trace = 2
        trace = 3
        return 4
    """,
        build_src=sources,
    )
    def test_try_finally(self):
        self.run_trace(4)

    @source(
        """
        trace = 0
        try:
            trace = 1
        except:
            trace = 1
        trace = 2
        return 3
    """,
        build_src=sources,
    )
    def test_try_except(self):
        self.run_trace(3)
        self.run_except_trace(3)

    @source(
        """
        trace = 0
        try:
            trace = 1
        except:
            trace = 2
        else:
            trace = 2
        trace = 3
        return 4
    """,
        build_src=sources,
    )
    def test_try_except_else(self):
        self.run_trace(4)
        self.run_except_trace(4)

    @source(
        """
        trace = 0
        try:
            trace = 1
        except:
            trace = 2
        else:
            trace = 2
        finally:
            trace = 3
        trace = 4
        return 5
    """,
        build_src=sources,
    )
    def test_try_except_else_finally(self):
        self.run_trace(5)
        self.run_except_trace(5)

    @source(
        """
        trace = 0
        try:
            trace = 1
        finally:
            trace = 2
            return 3
        trace = 0
    """,
        build_src=sources,
    )
    def test_try_finally_return(self):
        self.run_trace(3)

    @source(
        """
        trace = 0
        try:
            return 1
        finally:
            trace = 2
        trace = 0
    """,
        build_src=sources,
    )
    def test_try_return_finally(self):
        self.run_trace(2)

    @source(
        """
        trace = 0
        try:
            trace = 1
        except:
            trace = 2
        else:
            return 2
        finally:
            trace = 3
        trace = 4
    """,
        build_src=sources,
    )
    def test_try_else_return_finally(self):
        self.run_trace(3)
        self.run_except_trace(4)

    @source(
        """
        trace = 0
        try:
            trace = 1
            raise StopIteration
        except TypeError:
            trace = 2
        trace = 3
    """,
        build_src=sources,
    )
    def test_try_raise(self):
        self.run_trace(1)
        self.run_except_trace(3)

    @source(
        """
        trace = 0
        try:
            trace = 1
            raise StopIteration
        finally:
            trace = 2
        trace = 3
    """,
        build_src=sources,
    )
    def test_try_raise_finally(self):
        self.run_trace(2)

    @source(
        """
        trace = 0
        try:
            trace = 1
            raise StopIteration
        except:
            trace = 2
        else:
            trace = 2
        trace = 3
    """,
        build_src=sources,
    )
    def test_try_raise_except(self):
        self.run_trace(3)
        self.run_except_trace(3)

    @source(
        """
        trace = 0
        try:
            trace = 1
            raise Exception
        except:
            trace = 2
        else:
            trace = 2
        finally:
            trace = 3
        trace = 4
    """,
        build_src=sources,
    )
    def test_try_raise_except_finally(self):
        self.run_trace(4)
        self.run_except_trace(4)

    @source(
        """
        trace = 0
        try:
            trace = 1
            return 2
        finally:
            trace = 3
        trace = 4
    """,
        build_src=sources,
    )
    def test_finally_return(self):
        self.run_trace(3)

    @source(
        """
        trace = 0
        try:
            trace = 1
            raise StopIteration
        except:
            trace = 2
            return 3
        finally:
            trace = 4
        trace = 0
    """,
        build_src=sources,
    )
    def test_try_raise_except_return_finally(self):
        self.run_trace(4)
        self.run_except_trace(4)

    @source(
        """
        trace = 0
        try:
            trace = 1
            raise Exception
        except:
            trace = 2
            raise ValueError
        finally:
            trace = 3
    """,
        build_src=sources,
    )
    def test_raise_in_exception_handler(self):
        self.run_trace(3)
        self.run_except_trace(3)

    @source(
        """
        trace = 0
        try:
            trace = 1
        finally:
            trace = 2
            raise Exception
        trace = 3
    """,
        build_src=sources,
    )
    def test_raise_in_final_block(self):
        self.run_trace(2)  # 3 is not reachable

    @source(
        """
        trace = 0
        try:
            trace = 1
        except:
            pass
        else:
            trace = 2
            raise Exception
        finally:
            trace = 3
        trace = 4
    """,
        build_src=sources,
    )
    def test_raise_in_else_block(self):
        self.run_trace(3)  # 4 is not reachable


class Test_NestedTry(Test_Try):
    @source(
        """
        trace = 0
        try:
            trace = 1
            try:
                trace = 2
            finally:
                trace = 3
        finally:
            trace = 4
        trace = 5
    """,
        build_src=Test_Try.sources,
    )
    def test_try_try_finally_finally(self):
        self.run_trace(5)

    @source(
        """
        trace = 0
        try:
            trace = 1
            try:
                raise ValueError
            except TypeError:
                trace = 0 # not reachable
        except:
            trace = 2
        trace = 3
    """,
        build_src=Test_Try.sources,
    )
    def test_try_try_raise_except(self):
        self.run_trace(3)

    @source(
        """
        trace = 0
        try:
            trace = 1
            try:
                trace = 2
                raise AttributeError
            except AttributeError:
                trace = 3
                raise TypeError
        except TypeError:
            trace = 4
        trace = 5
    """,
        build_src=Test_Try.sources,
    )
    def test_try_try_raise_except_raise_except(self):
        self.run_trace(5)

    @source(
        """
        trace = 0
        try:
            trace = 1
            try:
                trace = 2
                try:
                    trace = 3
                    raise TypeError
                except ValueError:
                    trace = 0
            except StopIteration:
                trace = 0
        except TypeError:
            trace = 4
        trace = 5
        
    """,
        build_src=Test_Try.sources,
    )
    def test_try_try_try_raise_except(self):
        self.run_trace(5)

    @source(
        """
        trace = 0
        try:
            trace = 1
            try:
                trace = 2
            except:
                trace = 0
            else:
                trace = 3
                raise Exception
        finally:
            trace = 4
        trace = 5
    """,
        build_src=Test_Try.sources,
    )
    def test_try_try_else_raise_finally(self):
        self.run_trace(4)

    @source(
        """
        trace = 0
        try:
            trace = 1
            try:
                trace = 2
            except:
                trace = -1
            else:
                trace = 3
                raise Exception
        except:
            trace = 4
        trace = 5
    """,
        build_src=Test_Try.sources,
    )
    def test_try_try_else_raise_except(self):
        self.run_trace(5)

    @source(
        """
        trace = 0
        try:
            trace = 1
        except:
            trace = -1
        else:
            trace = 2
            try:
                trace = 3
                raise ValueError
            except:
                trace = 4
                raise TypeError
        finally:
            trace = 5
        trace = 6
    """,
        build_src=Test_Try.sources,
    )
    def test_try_else_try_raise_except_raise_finally(self):
        self.run_trace(5)

    @source(
        """
        trace = 0
        try:
            try:
                trace = 1
                raise Exception
            except:
                trace = 2
                try:
                    trace = 3
                    raise ValueError
                except:
                    trace = 4
                    raise TypeError
        except TypeError:
            trace = 5
        trace = 6
    """,
        build_src=Test_Try.sources,
    )
    def test_try_try_except_try_raise_finally_except(self):
        self.run_trace(6)

    @source(
        """
        trace = 0
        try:
            trace = 1
            try:
                trace = 2
            finally:
                trace = 3
                raise TypeError
        except TypeError:
            trace = 4
        trace = 5
    """,
        build_src=Test_Try.sources,
    )
    def test_try_try_finally_raise_except(self):
        self.run_trace(5)


if __name__ == "__main__":
    unittest.main()
