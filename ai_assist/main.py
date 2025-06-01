import argparse
import logging
import os
from pathlib import Path

from search_engine import index_project, index_project_incremental

# MCP-compliant logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def setup_argparse():
    """Configure command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Codebase indexing tool for MCP code search server."
    )
    parser.add_argument(
        "--project-path",
        type=Path,
        default=Path(os.getenv("MCP_PROJECT_PATH", os.getcwd())),
        help="Path to the project directory to index (default: MCP_PROJECT_PATH or current directory).",
    )
    parser.add_argument(
        "--action",
        choices=["reindex", "full-reindex"],
        default="reindex",
        help="Action to perform: reindex (incremental) or full-reindex (full indexing).",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose logging."
    )
    return parser


def main():
    """Main entry point for command-line indexing."""
    parser = setup_argparse()
    args = parser.parse_args()

    # Adjust logging level if verbose
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info(f"Starting indexing for project at {args.project_path}")
    try:
        if args.action == "reindex":
            index_project_incremental(args.project_path)
            logger.info("Incremental indexing completed successfully.")
        elif args.action == "full-reindex":
            index_project(args.project_path)
            logger.info("Full indexing completed successfully.")
    except Exception as e:
        logger.error(f"Indexing failed: {e}")
        raise


if __name__ == "__main__":
    main()
