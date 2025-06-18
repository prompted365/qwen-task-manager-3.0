#!/usr/bin/env python3
"""Command line interface for the Component Registry."""

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from agents.component_registry import ComponentRegistry
from config.uss_config import get_config


def get_registry(db_path: str = None) -> ComponentRegistry:
    """Instantiate registry using configuration unless path provided."""
    if db_path is None:
        config = get_config()
        db_path = config.database.db_path
    return ComponentRegistry(Path(db_path))


def cmd_register(args: argparse.Namespace) -> None:
    registry = get_registry(args.db)
    info: Dict[str, Any] = {
        "name": args.name,
        "type": args.type,
        "file_path": args.file_path,
    }
    component_id = registry.register_component(info)
    print(component_id)


def cmd_list(args: argparse.Namespace) -> None:
    registry = get_registry(args.db)
    components = registry.list_components(status=args.status, component_type=args.type)
    for comp in components:
        print(f"{comp['id']}\t{comp['name']}\t{comp['type']}\t{comp['status']}")


def cmd_show(args: argparse.Namespace) -> None:
    registry = get_registry(args.db)
    comp = registry.get_component(args.id)
    if not comp:
        print("Component not found")
        return
    print(json.dumps(comp, indent=2))
    if args.story:
        story = registry.get_component_story(args.id)
        if story:
            print("\nUser Story:")
            print(json.dumps(story, indent=2))
        else:
            print("No story found")


def cmd_flag(args: argparse.Namespace) -> None:
    registry = get_registry(args.db)
    flag_id = registry.flag_component(args.id, args.level, args.details)
    print(flag_id)


def cmd_resolve(args: argparse.Namespace) -> None:
    registry = get_registry(args.db)
    success = registry.resolve_flag(args.id, resolved_by=args.by)
    if success:
        print("Flag resolved")
    else:
        print("No unresolved flag found")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Component Registry CLI")
    parser.add_argument("--db", help="Path to registry database")
    subparsers = parser.add_subparsers(dest="command")

    # register
    p_reg = subparsers.add_parser("register", help="Register a component")
    p_reg.add_argument("--name", required=True, help="Component name")
    p_reg.add_argument("--type", default="module", help="Component type")
    p_reg.add_argument("--file-path", dest="file_path", help="File path")
    p_reg.set_defaults(func=cmd_register)

    # list
    p_list = subparsers.add_parser("list", help="List components")
    p_list.add_argument("--status", default="active", help="Component status filter")
    p_list.add_argument("--type", help="Component type filter")
    p_list.set_defaults(func=cmd_list)

    # show
    p_show = subparsers.add_parser("show", help="Show component details")
    p_show.add_argument("id", help="Component ID")
    p_show.add_argument("--story", action="store_true", help="Show latest user story")
    p_show.set_defaults(func=cmd_show)

    # flag
    p_flag = subparsers.add_parser("flag", help="Flag a component")
    p_flag.add_argument("id", help="Component ID")
    p_flag.add_argument("level", help="Flag level")
    p_flag.add_argument("details", help="Flag details")
    p_flag.set_defaults(func=cmd_flag)

    # resolve
    p_resolve = subparsers.add_parser("resolve", help="Resolve a flag")
    p_resolve.add_argument("id", help="Component ID")
    p_resolve.add_argument("--by", help="Resolver name")
    p_resolve.set_defaults(func=cmd_resolve)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
