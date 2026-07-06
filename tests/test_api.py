# -*- coding: utf-8 -*-

from shsk_coding_agent_docs import api


def test():
    _ = api


if __name__ == "__main__":
    from shsk_coding_agent_docs.tests import run_cov_test

    run_cov_test(
        __file__,
        "shsk_coding_agent_docs.api",
        preview=False,
    )
