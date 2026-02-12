"""
CLI entry point for the Auto-Revision Epistemic Engine.

Enables: python -m auto_revision_epistemic_engine
"""

import argparse
import json
import sys
import tempfile
from typing import Optional


def cmd_run(args: argparse.Namespace) -> int:
    """Execute the 8-phase pipeline with configurable inputs."""
    from auto_revision_epistemic_engine import AutoRevisionEngine

    # Parse inputs from JSON string or file
    inputs = {}
    if args.inputs:
        inputs = json.loads(args.inputs)
    elif args.inputs_file:
        with open(args.inputs_file, "r") as f:
            config = json.load(f)
            inputs = config.get("inputs", config)

    # Extract pipeline config from file if provided
    pipeline_id = args.pipeline_id
    random_seed: Optional[int] = args.seed
    enable_hrg = not args.no_hrg
    enable_ethics = not args.no_ethics

    if args.inputs_file:
        with open(args.inputs_file, "r") as f:
            config = json.load(f)
            pipeline_id = config.get("pipeline_id", pipeline_id)
            random_seed = config.get("random_seed", random_seed)
            hrg_cfg = config.get("hrg_config", {})
            if hrg_cfg.get("auto_approve") is not None:
                enable_hrg = True
            ethics_cfg = config.get("ethics_config", {})
            if ethics_cfg.get("enabled") is not None:
                enable_ethics = ethics_cfg["enabled"]

    engine = AutoRevisionEngine(
        pipeline_id=pipeline_id,
        random_seed=random_seed,
        enable_hrg=enable_hrg,
        enable_ethics_audit=enable_ethics,
        audit_log_dir=args.audit_dir or tempfile.mkdtemp(prefix="are_audit_"),
        state_dir=args.state_dir or tempfile.mkdtemp(prefix="are_state_"),
    )

    result = engine.execute(inputs=inputs)
    print(json.dumps(result, indent=2, default=str))
    return 0 if result.get("success") else 1


def cmd_status(args: argparse.Namespace) -> int:
    """Show pipeline status after initialization."""
    from auto_revision_epistemic_engine import AutoRevisionEngine

    engine = AutoRevisionEngine(
        pipeline_id=args.pipeline_id,
        random_seed=args.seed,
        audit_log_dir=args.audit_dir or tempfile.mkdtemp(prefix="are_audit_"),
        state_dir=args.state_dir or tempfile.mkdtemp(prefix="are_state_"),
    )

    status = engine.get_status()
    print(json.dumps(status, indent=2, default=str))
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    """Verify audit chain integrity."""
    from auto_revision_epistemic_engine import AutoRevisionEngine

    engine = AutoRevisionEngine(
        pipeline_id=args.pipeline_id or "audit-check",
        audit_log_dir=args.audit_dir or tempfile.mkdtemp(prefix="are_audit_"),
        state_dir=args.state_dir or tempfile.mkdtemp(prefix="are_state_"),
    )

    # Run pipeline first if requested
    if args.after_run:
        engine.execute(inputs={"data": {"source": "audit-verification"}})

    audit_trail = engine.get_audit_trail()
    print(json.dumps(audit_trail, indent=2, default=str))

    if audit_trail["chain_valid"]:
        print("\n[OK] Audit chain integrity verified.", file=sys.stderr)
        return 0
    else:
        print("\n[FAIL] Audit chain integrity BROKEN.", file=sys.stderr)
        return 1


def cmd_demo(args: argparse.Namespace) -> int:
    """Run a demonstration with sample data."""
    import tempfile
    from auto_revision_epistemic_engine import AutoRevisionEngine

    audit_dir = tempfile.mkdtemp(prefix="are_demo_audit_")
    state_dir = tempfile.mkdtemp(prefix="are_demo_state_")

    print(json.dumps({"stage": "init", "message": "Initializing demo engine..."}, indent=2))

    engine = AutoRevisionEngine(
        pipeline_id="demo-eight-phase",
        random_seed=42,
        enable_hrg=True,
        enable_ethics_audit=True,
        enable_resource_tracking=True,
        audit_log_dir=audit_dir,
        state_dir=state_dir,
    )

    # Pin a demo model for reproducibility
    engine.pin_model("demo-model", "v1.0.0-demo")

    # Add a custom ethical axiom
    engine.add_ethical_axiom(
        axiom_id="DEMO_001",
        category="TRANSPARENCY",
        statement="Demo operations must be fully observable",
        weight=1.0,
    )

    print(json.dumps({"stage": "execute", "message": "Executing 8-phase pipeline..."}, indent=2))

    result = engine.execute(inputs={
        "data": {"records": 100, "format": "demo"},
        "source": "demo-cli",
    })

    print(json.dumps({"stage": "result", "pipeline_result": result}, indent=2, default=str))

    # Gather all reports
    reports = {
        "stage": "reports",
        "status": engine.get_status(),
        "audit_trail": engine.get_audit_trail(),
        "reproducibility": engine.get_reproducibility_info(),
        "resource_report": engine.get_resource_report(),
        "ethics_report": engine.get_ethics_report(),
        "hrg_report": engine.get_hrg_report(),
    }

    print(json.dumps(reports, indent=2, default=str))
    print(json.dumps({
        "stage": "complete",
        "message": "Demo completed successfully.",
        "audit_dir": audit_dir,
        "state_dir": state_dir,
    }, indent=2))

    return 0 if result.get("success") else 1


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="auto-revision-epistemic-engine",
        description=(
            "Auto-Revision Epistemic Engine (v4.2) -- "
            "A self-governing orchestration framework with 8 phases "
            "and 4 human oversight gates."
        ),
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- run ---
    run_parser = subparsers.add_parser("run", help="Execute the 8-phase pipeline")
    run_parser.add_argument(
        "--pipeline-id", default="cli-pipeline",
        help="Unique pipeline identifier (default: cli-pipeline)",
    )
    run_parser.add_argument(
        "--seed", type=int, default=None,
        help="Random seed for reproducibility",
    )
    run_parser.add_argument(
        "--inputs", type=str, default=None,
        help='JSON string of pipeline inputs (e.g. \'{"data": {"records": 50}}\')',
    )
    run_parser.add_argument(
        "--inputs-file", type=str, default=None,
        help="Path to JSON config file with pipeline inputs",
    )
    run_parser.add_argument("--no-hrg", action="store_true", help="Disable HRG gates")
    run_parser.add_argument("--no-ethics", action="store_true", help="Disable ethics audits")
    run_parser.add_argument("--audit-dir", type=str, default=None, help="Audit log directory")
    run_parser.add_argument("--state-dir", type=str, default=None, help="State snapshot directory")

    # --- status ---
    status_parser = subparsers.add_parser("status", help="Show pipeline status")
    status_parser.add_argument("--pipeline-id", default="status-check", help="Pipeline identifier")
    status_parser.add_argument("--seed", type=int, default=None, help="Random seed")
    status_parser.add_argument("--audit-dir", type=str, default=None, help="Audit log directory")
    status_parser.add_argument("--state-dir", type=str, default=None, help="State snapshot directory")

    # --- audit ---
    audit_parser = subparsers.add_parser("audit", help="Verify audit chain integrity")
    audit_parser.add_argument("--pipeline-id", default=None, help="Pipeline identifier")
    audit_parser.add_argument("--after-run", action="store_true", help="Run pipeline first, then verify")
    audit_parser.add_argument("--audit-dir", type=str, default=None, help="Audit log directory")
    audit_parser.add_argument("--state-dir", type=str, default=None, help="State snapshot directory")

    # --- demo ---
    subparsers.add_parser("demo", help="Run a demonstration with sample data")

    return parser


def main() -> int:
    """Main entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    dispatch = {
        "run": cmd_run,
        "status": cmd_status,
        "audit": cmd_audit,
        "demo": cmd_demo,
    }

    handler = dispatch.get(args.command)
    if handler is None:
        parser.print_help()
        return 1

    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
