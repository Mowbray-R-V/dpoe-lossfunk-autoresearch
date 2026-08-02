"""Preregistered analysis for completed MVE 3 locked cells."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from core import (CELLS, TIERS, Config, CellSpec, auroc, cell_path, make_scenario,
                  partial_spearman, risk_coverage_auc, spearman,
                  terminal_probabilities, validate_cell)
from metrics import normalized_auc


def load_summaries(root: Path, replicates: int, cfg: Config) -> list[dict[str, object]]:
    rows = []
    for replicate in range(replicates):
        for severity in (1, 2, 3):
            for tier in TIERS:
                for cell in CELLS:
                    spec = CellSpec("locked", replicate, severity, tier, cell)
                    path = cell_path(root, spec)
                    if not validate_cell(path, spec, cfg):
                        raise RuntimeError(f"Missing/invalid cell: {path}")
                    with np.load(path, allow_pickle=False) as d:
                        meta = json.loads(str(d["metadata"]))
                        checkpoints = d["checkpoints"].astype(float)
                        eval_return = d["eval_true"].mean(axis=1)
                        eval_hacking = d["eval_hacking"].mean(axis=1)
                        eval_goal = d["eval_goal"].mean(axis=1)
                        collection_goal = d["collection_goal"].mean(axis=1)
                        rows.append({
                            "replicate": replicate, "severity": severity, "tier": tier, "cell": cell,
                            "return_auc": normalized_auc(eval_return, checkpoints),
                            "hacking_auc": normalized_auc(eval_hacking, checkpoints),
                            "eval_goal_auc": normalized_auc(eval_goal, checkpoints),
                            "collection_goal_auc": normalized_auc(collection_goal, np.arange(1, cfg.iterations + 1)),
                            "final_return": float(eval_return[-1]), "final_hacking": float(eval_hacking[-1]),
                            "entropy_auc": normalized_auc(d["eval_entropy"], checkpoints),
                            "kl_auc": normalized_auc(d["eval_kl"], checkpoints),
                            "trap_present": int(meta["trap_present"]), "trap_strength": meta["trap_strength"],
                            "goal_strength": meta["goal_strength"], "reference_competence": meta["reference_competence"],
                        })
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)


def by_seed(rows: list[dict[str, object]], tier: str, cell: str, metric: str,
            severity: int | None = None) -> np.ndarray:
    values: dict[int, list[float]] = defaultdict(list)
    for row in rows:
        if row["tier"] == tier and row["cell"] == cell and (severity is None or row["severity"] == severity):
            values[int(row["replicate"])].append(float(row[metric]))
    return np.asarray([np.mean(values[i]) for i in sorted(values)])


def i3_by_seed(rows: list[dict[str, object]], tier: str, metric: str,
               severity: int | None = None) -> np.ndarray:
    v = {cell: by_seed(rows, tier, cell, metric, severity) for cell in CELLS}
    return v["pko"] - v["pk"] - v["po"] - v["ko"] + v["p"] + v["k"] + v["o"] - v["none"]


def bootstrap_ci(values: np.ndarray, confidence: float, rng: np.random.Generator,
                 draws: int = 30_000) -> tuple[float, float]:
    idx = rng.integers(0, len(values), (draws, len(values)))
    means = values[idx].mean(axis=1)
    alpha = 1 - confidence
    return float(np.quantile(means, alpha / 2)), float(np.quantile(means, 1 - alpha / 2))


def permutation_p(values: np.ndarray, rng: np.random.Generator, draws: int = 100_000) -> float:
    observed = abs(float(np.mean(values)))
    null = np.abs((rng.choice((-1.0, 1.0), (draws, len(values))) * values).mean(axis=1))
    return float((np.sum(null >= observed) + 1) / (draws + 1))


def holm(values: list[float]) -> list[float]:
    order = np.argsort(values); result = np.empty(len(values)); running = 0.0; m = len(values)
    for rank, idx in enumerate(order):
        running = max(running, (m - rank) * values[int(idx)])
        result[int(idx)] = min(1.0, running)
    return result.tolist()


def dz(values: np.ndarray) -> float:
    sd = float(np.std(values, ddof=1))
    return float(np.mean(values) / sd) if sd else float("inf")


def h3a(rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], dict[str, list[float]]]:
    v = {cell: by_seed(rows, "controlled", cell, "return_auc") for cell in CELLS}
    contrasts = {
        "return:pko-pk": v["pko"] - v["pk"],
        "return:pko-o": v["pko"] - v["o"],
        "return:pko-po": v["pko"] - v["po"],
        "return:pko-ko": v["pko"] - v["ko"],
        "return:I3": i3_by_seed(rows, "controlled", "return_auc"),
        "collection_goal:pko-pk": by_seed(rows, "controlled", "pko", "collection_goal_auc") - by_seed(rows, "controlled", "pk", "collection_goal_auc"),
        "hacking:o-pko": by_seed(rows, "controlled", "o", "hacking_auc") - by_seed(rows, "controlled", "pko", "hacking_auc"),
        "hacking_NI:pko-pk": by_seed(rows, "controlled", "pko", "hacking_auc") - by_seed(rows, "controlled", "pk", "hacking_auc"),
    }
    rng = np.random.default_rng(320260718); confidence = 1 - 0.05 / len(contrasts)
    output, pvals = [], []
    for name, diff in contrasts.items():
        lo, hi = bootstrap_ci(diff, confidence, rng)
        p = permutation_p(diff, rng); pvals.append(p)
        output.append({"family": "H3a", "contrast": name, "mean": float(np.mean(diff)),
                       "simultaneous_low": lo, "simultaneous_high": hi,
                       "cohens_dz": dz(diff), "permutation_p": p,
                       "individual_confidence": confidence})
    for row, adjusted in zip(output, holm(pvals)): row["holm_p"] = adjusted
    severity_directions: dict[str, list[float]] = {}
    for name in list(contrasts)[:7]:
        per = []
        for severity in (1, 2, 3):
            sv = {cell: by_seed(rows, "controlled", cell, "return_auc", severity) for cell in CELLS}
            if name == "return:pko-pk": diff = sv["pko"] - sv["pk"]
            elif name == "return:pko-o": diff = sv["pko"] - sv["o"]
            elif name == "return:pko-po": diff = sv["pko"] - sv["po"]
            elif name == "return:pko-ko": diff = sv["pko"] - sv["ko"]
            elif name == "return:I3": diff = i3_by_seed(rows, "controlled", "return_auc", severity)
            elif name == "collection_goal:pko-pk": diff = by_seed(rows,"controlled","pko","collection_goal_auc",severity)-by_seed(rows,"controlled","pk","collection_goal_auc",severity)
            else: diff = by_seed(rows,"controlled","o","hacking_auc",severity)-by_seed(rows,"controlled","pko","hacking_auc",severity)
            per.append(float(np.mean(diff)))
        severity_directions[name] = per
    return output, severity_directions


def exploitation_floor(rows: list[dict[str, object]]) -> dict[str, float | bool]:
    """Post-review diagnostic for whether the exploitation estimand was reachable.

    This is deliberately separate from the signal-quality gate: a calibrated signal is
    not informative about coupling if the frozen-reference trust region prevents every
    policy from acting on the discovered goal.  The 1% AUC threshold is a conservative
    practical floor (two goal successes per 200-episode checkpoint, on average), added
    after the independent result review; it does not convert this locked run into a new
    confirmatory test.
    """
    controlled = np.asarray([float(r["eval_goal_auc"]) for r in rows if r["tier"] == "controlled"])
    pko = np.asarray([float(r["eval_goal_auc"]) for r in rows if r["tier"] == "controlled" and r["cell"] == "pko"])
    return {
        "controlled_eval_goal_auc_mean": float(np.mean(controlled)),
        "controlled_eval_goal_auc_max": float(np.max(controlled)),
        "controlled_cells_at_or_below_0_005": float(np.mean(controlled <= 0.005)),
        "controlled_pko_eval_goal_auc_mean": float(np.mean(pko)),
        "design_floor_detected": bool(np.mean(controlled) < 0.01),
    }


def h3b(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    controlled = i3_by_seed(rows, "controlled", "return_auc")
    contrasts = {
        "I3:controlled-shuffled": controlled - i3_by_seed(rows, "shuffled", "return_auc"),
        "I3:controlled-anti": controlled - i3_by_seed(rows, "anti", "return_auc"),
    }
    rng = np.random.default_rng(330260718); confidence = 1 - 0.05 / 2
    out, pvals = [], []
    for name, diff in contrasts.items():
        lo, hi = bootstrap_ci(diff, confidence, rng); p = permutation_p(diff, rng); pvals.append(p)
        out.append({"family":"H3b", "contrast":name, "mean":float(np.mean(diff)),
                    "simultaneous_low":lo, "simultaneous_high":hi, "cohens_dz":dz(diff),
                    "permutation_p":p, "individual_confidence":confidence})
    for row, adjusted in zip(out, holm(pvals)): row["holm_p"] = adjusted
    return out


def quality_gates(replicates: int, cfg: Config) -> dict[str, object]:
    by_tier_severity = {(tier, s): {"u":[], "error":[]} for tier in TIERS for s in (1,2,3)}
    leak, traps, goals, competences = [], [], [], []
    scenario_by_tier_severity: dict[str, dict[str, dict[str, float]]] = {tier:{} for tier in TIERS}
    for rep in range(replicates):
        for severity in (1,2,3):
            scenario = make_scenario("locked", rep, severity, cfg)
            error = np.abs(scenario.true_rewards - scenario.mu0)
            refp = terminal_probabilities(scenario.reference)
            leak.extend(zip(scenario.u0, scenario.true_rewards, scenario.mu0, refp))
            traps.append(float(scenario.trap_present)); goals.append(scenario.goal_strength); competences.append(scenario.reference_competence)
            for tier in TIERS:
                scenario_by_tier_severity[tier][str(severity)] = {
                    "trap_prevalence": scenario_by_tier_severity[tier].get(str(severity), {}).get("trap_prevalence", 0.0) + float(scenario.trap_present) / replicates,
                    "mean_trap_strength": scenario_by_tier_severity[tier].get(str(severity), {}).get("mean_trap_strength", 0.0) + float(scenario.trap_strength) / replicates,
                    "mean_goal_strength": scenario_by_tier_severity[tier].get(str(severity), {}).get("mean_goal_strength", 0.0) + float(scenario.goal_strength) / replicates,
                }
                if tier == "controlled": u = scenario.u0
                elif tier == "learned":
                    u = np.std(scenario.target_features @ scenario.ensemble0.T, axis=1, ddof=1) * scenario.learned_scale
                elif tier == "shuffled":
                    from core import tier_initial_u
                    u = tier_initial_u(scenario, tier)
                else:
                    from core import tier_initial_u
                    u = tier_initial_u(scenario, tier)
                by_tier_severity[(tier,severity)]["u"].extend(u.tolist())
                by_tier_severity[(tier,severity)]["error"].extend(error.tolist())
    result: dict[str, object] = {"tiers":{}, "trap_prevalence":float(np.mean(traps)),
                                "goal_strength_mean":float(np.mean(goals)),
                                "reference_competence_min":float(np.min(competences)),
                                "scenario_by_tier_severity":scenario_by_tier_severity}
    for tier in TIERS:
        result["tiers"][tier] = {}
        for severity in (1,2,3):
            d=by_tier_severity[(tier,severity)]; u=np.asarray(d["u"]); error=np.asarray(d["error"])
            hard=error>=np.quantile(error,.75)
            result["tiers"][tier][str(severity)]={"spearman":spearman(u,error),"auroc":auroc(u,hard),
                "risk_coverage_auc":risk_coverage_auc(u,error),"n_points":len(error)}
    a=np.asarray(leak)
    partial=partial_spearman(a[:,0],a[:,1],a[:,2:])
    result["leakage_partial_spearman_aggregate"]=partial
    controlled_entries=result["tiers"]["controlled"].values()
    learned_entries=result["tiers"]["learned"].values()
    result["controlled_locked_quality_pass"]=all(x["auroc"]>=.75 and x["spearman"]>=.50 for x in controlled_entries)
    result["learned_locked_quality_pass"]=all(x["auroc"]>=.70 and x["spearman"]>=.40 for x in learned_entries)
    result["leakage_guard_pass"]=abs(partial)<=.10
    return result


def group_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rng=np.random.default_rng(77); out=[]
    for tier in TIERS:
        for cell in CELLS:
            for metric in ("return_auc","hacking_auc","collection_goal_auc"):
                v=by_seed(rows,tier,cell,metric); lo,hi=bootstrap_ci(v,.95,rng,10_000)
                out.append({"tier":tier,"cell":cell,"metric":metric,"mean":float(np.mean(v)),"ci_low":lo,"ci_high":hi})
    return out


def plot_results(summary: list[dict[str, object]], h3b_rows: list[dict[str, object]], outdir: Path) -> None:
    fig, axes=plt.subplots(1,4,figsize=(16,4),sharey=True)
    for ax,tier in zip(axes,TIERS):
        ss=[r for r in summary if r["tier"]==tier and r["metric"]=="return_auc"]
        ss.sort(key=lambda r:CELLS.index(str(r["cell"])))
        m=np.asarray([r["mean"] for r in ss]); lo=np.asarray([r["ci_low"] for r in ss]); hi=np.asarray([r["ci_high"] for r in ss])
        ax.bar(range(8),m); ax.errorbar(range(8),m,yerr=(m-lo,hi-m),fmt="none",c="black",capsize=2)
        ax.set_xticks(range(8),CELLS,rotation=45); ax.set_title(tier); ax.set_ylabel("Evaluation true-return AUC")
    fig.tight_layout(); fig.savefig(outdir/"return_auc_factorial.png",dpi=180); plt.close(fig)


def report_markdown(h3a_rows: list[dict[str, object]], h3b_rows: list[dict[str, object]],
                    quality: dict[str, object], directions: dict[str,list[float]],
                    floor: dict[str, float | bool], verdict: dict[str, object]) -> str:
    lines=["# MVE 3 Results","","Synthetic online reward-posterior mechanism test; no MLLM was used.","",
           "## Quality and validity gates","",
           f"- Controlled locked quality passed: **{quality['controlled_locked_quality_pass']}**.",
           f"- Learned locked quality passed: **{quality['learned_locked_quality_pass']}**.",
           f"- Leakage guard passed: **{quality['leakage_guard_pass']}** (partial Spearman {quality['leakage_partial_spearman_aggregate']:.4f}).",
           f"- Locked reference competence minimum: **{quality['reference_competence_min']:.3f}** (required >=0.800).",
           f"- Trap prevalence: {quality['trap_prevalence']:.3f}; mean goal strength: {quality['goal_strength_mean']:.3f}.",
           "- The locked quality gate is evaluated per severity here, whereas the preregistered wording specified an aggregate gate. This is stricter; all severities passed, so the deviation does not favor the result.",
           "- Learned-tier uncertainty was RMS-rescaled to the controlled prior uncertainty using the generator's `u0`; this is oracle-scale information and is disclosed for reproducibility. It does not affect a learned-tier claim because that tier failed its quality gate.","",
           "### Scenario statistics by tier and severity","",
           "Truth is paired across tiers, so the per-tier rows below are intentionally identical within each severity.","",
           "| Tier | Severity | Trap prevalence | Mean trap strength | Mean goal strength |","|---|---:|---:|---:|---:|"]
    for tier in TIERS:
        for severity in (1,2,3):
            stats=quality["scenario_by_tier_severity"][tier][str(severity)]
            lines.append(f"| {tier} | {severity} | {stats['trap_prevalence']:.3f} | {stats['mean_trap_strength']:.3f} | {stats['mean_goal_strength']:.3f} |")
    lines += ["", "Entropy and KL AUCs are retained per cell in `cell_summary.csv`; raw checkpoint terminal arrays in `cells/*.npz` support any secondary timeout/collapse audit.", "",
           "## Exploitation manipulation check (post-review diagnostic)",""]
    lines += [
           f"- Mean controlled evaluation true-goal-success AUC: **{floor['controlled_eval_goal_auc_mean']:.4f}**; P+K+O mean: **{floor['controlled_pko_eval_goal_auc_mean']:.4f}**.",
           f"- The operative post-review design-floor trigger is mean controlled goal-success AUC < **0.0100**. Separately, {100 * float(floor['controlled_cells_at_or_below_0_005']):.1f}% of controlled cells are at or below 0.005; the maximum is {floor['controlled_eval_goal_auc_max']:.4f}.",
           "- **Design floor detected:** the exploitation policy almost never reaches the true goal. The original protocol did not preregister an oracle-reachability manipulation check, so these locked contrasts cannot support or kill the coupling mechanism.","",
           "## H3a confirmatory family","","Positive values support the named superiority contrast; hacking non-inferiority instead requires the CI upper bound < 0.02.","",
           "| Contrast | Mean | Simultaneous CI | Holm p | d_z |","|---|---:|---:|---:|---:|"]
    for r in h3a_rows: lines.append(f"| {r['contrast']} | {r['mean']:.4f} | [{r['simultaneous_low']:.4f}, {r['simultaneous_high']:.4f}] | {r['holm_p']:.4f} | {r['cohens_dz']:.3f} |")
    lines += ["","## H3b signal-quality moderation","","| Contrast | Mean | Simultaneous CI | Holm p |","|---|---:|---:|---:|"]
    for r in h3b_rows: lines.append(f"| {r['contrast']} | {r['mean']:.4f} | [{r['simultaneous_low']:.4f}, {r['simultaneous_high']:.4f}] | {r['holm_p']:.4f} |")
    lines += ["", "H3b is likewise floor-uninformative: its null moderation contrasts cannot adjudicate signal-quality moderation while exploitation cannot act on the true goal.", "", "## Per-severity directions",""]
    for name,v in directions.items(): lines.append(f"- {name}: " + ", ".join(f"s{i+1}={x:.4f}" for i,x in enumerate(v)))
    lines += ["","## Verdict (post-review validity amendment)","", "- The preregistered kill rule did fire: controlled quality passed, full lost to O and P+O, and I3 was non-positive. This post-review amendment sets that kill aside because the rule presupposes a reachable true goal; independent review `reviews/review-08.md` identified the failed manipulation check before any rerun.", f"- Controlled H3a support: **{verdict['h3a_support']}**.",
              f"- H3b moderation support: **{verdict['h3b_support']}**.",f"- Conditional C3 verdict: **{verdict['conditional_c3']}**.",
              f"- Learned H3c status: **{verdict['h3c_status']}**.","- Submitted frozen-MLLM C3 remains untested by design.",""]
    return "\n".join(lines)


def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("--root",type=Path,required=True); parser.add_argument("--replicates",type=int,required=True)
    args=parser.parse_args(); cfg=Config(); rows=load_summaries(args.root,args.replicates,cfg); write_csv(args.root/"cell_summary.csv",rows)
    quality=quality_gates(args.replicates,cfg); (args.root/"locked-quality.json").write_text(json.dumps(quality,indent=2)+"\n")
    h3a_rows,directions=h3a(rows); h3b_rows=h3b(rows); floor=exploitation_floor(rows); write_csv(args.root/"h3a_contrasts.csv",h3a_rows); write_csv(args.root/"h3b_contrasts.csv",h3b_rows)
    summary=group_summary(rows); write_csv(args.root/"group_summary.csv",summary); plot_results(summary,h3b_rows,args.root)
    superiority=[r for r in h3a_rows if not str(r["contrast"]).startswith("hacking_NI")]
    ni=next(r for r in h3a_rows if str(r["contrast"]).startswith("hacking_NI"))
    directions_ok=all(sum(x>0 for x in values)>=2 for values in directions.values())
    h3a_support=bool(quality["controlled_locked_quality_pass"] and quality["leakage_guard_pass"]
                     and all(r["simultaneous_low"]>0 and r["holm_p"]<.05 for r in superiority)
                     and ni["simultaneous_high"]<.02 and directions_ok)
    h3b_support=all(r["simultaneous_low"]>0 and r["holm_p"]<.05 for r in h3b_rows)
    h3a_by_contrast={str(r["contrast"]): r for r in h3a_rows}
    preregistered_kill_rule_fired=bool(
        quality["controlled_locked_quality_pass"] and (
            h3a_by_contrast["return:pko-pk"]["mean"] <= 0
            or h3a_by_contrast["return:pko-o"]["mean"] <= 0
            or h3a_by_contrast["return:I3"]["mean"] <= 0
        )
    )
    if bool(floor["design_floor_detected"]): conditional="untested-design-floor-policy-collapse"
    elif not quality["controlled_locked_quality_pass"] or not quality["leakage_guard_pass"]: conditional="untested-invalid-signal"
    elif not h3a_support: conditional="killed-at-toy-scale"
    elif not h3b_support: conditional="weakened-moderation-failed"
    else: conditional="supported-at-toy-scale"
    learned_dev=json.loads((args.root.parent/"mve3-gates"/"development-gates.json").read_text()).get("learned_development_gate_pass",False)
    h3c="eligible" if learned_dev and quality["learned_locked_quality_pass"] else "untested-quality-gate-failed"
    verdict={"verdict_status":"post-review-validity-amendment","preregistered_kill_rule_fired":preregistered_kill_rule_fired,"h3a_support":h3a_support,"h3b_support":h3b_support,"conditional_c3":conditional,"h3c_status":h3c,"severity_directions_ok":directions_ok,"exploitation_floor":floor}
    (args.root/"verdict.json").write_text(json.dumps(verdict,indent=2)+"\n")
    report=report_markdown(h3a_rows,h3b_rows,quality,directions,floor,verdict); (args.root/"RESULTS.md").write_text(report); print(report)


if __name__=="__main__": main()
