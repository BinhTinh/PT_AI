"""
Attack Type Framework - dinh nghia tinh mechanism/evidence cho tung ma ASI01-ASI10.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple


@dataclass(frozen=True)
class AttackTypeDefinition:
    asi_id: str
    attack_type: str
    mechanism_fields: Dict[str, str]
    evidence_fields: Dict[str, str]


_FRAMEWORK: Tuple[AttackTypeDefinition, ...] = (
    AttackTypeDefinition(
        "ASI01", "content_injection",
        {
            "injection_vector": "Kenh chua chi thi an: tai lieu/RAG, email/calendar, "
                                 "tool output gia mao, agent-to-agent message gia, "
                                 "du lieu ngoai bi dau doc.",
            "hidden_instruction_payload": "Noi dung chi thi an cu the duoc nhung vao injection_vector.",
            "entry_step": "Buoc nao trong luong xu ly agent se cham toi injection_vector nay "
                           "(agent tu doc, khong phai nguoi dung go tay).",
        },
        {
            "deviated_action_evidence": "Event the hien agent da lech muc tieu/hanh dong goc "
                                         "do chi thi an gay ra.",
            "baseline_action_reference": "Hanh dong/ket qua ky vong NEU KHONG bi hijack, "
                                          "dung de so sanh state-diff.",
        },
    ),
    AttackTypeDefinition(
        "ASI02", "tool_misuse",
        {
            "authorized_tool_chain": "Chuoi tool hop le, dung thu tu ky vong agent goi.",
            "misuse_pattern": "over-privileged access / over-scoped access / "
                               "unvalidated input forwarding / loop amplification / "
                               "external data tool poisoning.",
            "trigger_input": "Input khoi phat chuoi nay, co the hoan toan khong chua "
                              "chi thi doc hai.",
        },
        {
            "tool_call_sequence_evidence": "Danh sach TOOL_CALL event ky vong xuat hien "
                                            "dung thu tu theo authorized_tool_chain.",
            "misuse_parameter_check": "Tham so cu the trong tool call the hien lam dung "
                                       "(vd: vuot pham vi cho phep).",
        },
    ),
    AttackTypeDefinition(
        "ASI03", "privilege_abuse",
        {
            "privilege_context": "Credential/context bi ke thua hoac tai dung "
                                  "(delegation, cached credential, forged persona).",
            "escalation_mechanism": "unscoped_inheritance / memory_based_retention / "
                                     "cross_agent_confused_deputy / toctou / synthetic_identity.",
            "target_privilege": "Quyen/hanh dong nang cao ma attacker huong toi.",
        },
        {
            "privilege_boundary_violation_evidence": "Event the hien hanh dong vuot qua "
                                                       "pham vi quyen duoc cap ban dau.",
            "identity_context_trace": "Bang chung duong di cua credential/context bi tai "
                                       "su dung sai cho.",
        },
    ),
    AttackTypeDefinition(
        "ASI04", "supply_chain_compromise",
        {
            "compromised_component": "Loai thanh phan ben thu ba bi gia mao/tampered: "
                                      "prompt template / tool descriptor / third-party agent / "
                                      "registry server / RAG plugin.",
            "tampering_method": "impersonation/typosquatting, descriptor injection, "
                                 "poisoned content, compromised registry.",
            "load_channel": "Cach/thoi diem target nap/tin tuong thanh phan nay "
                             "(runtime discovery, update channel).",
        },
        {
            "component_load_evidence": "Event the hien target da nap/goi thanh phan bi tampered.",
            "resulting_action_evidence": "Event/state-diff the hien hanh vi doc hai xay ra "
                                          "do thanh phan do.",
        },
    ),
    AttackTypeDefinition(
        "ASI05", "unexpected_code_execution",
        {
            "execution_vector": "injection vao shell, code hallucination, unsafe "
                                 "deserialization, tool-chain nap code.",
            "payload_code": "Doan ma/lenh cu the duoc thuc thi.",
            "execution_context": "Noi ma thuc thi: workspace agent, container, host, memory eval.",
        },
        {
            "code_execution_evidence": "Event the hien mot hanh dong EXEC/shell/eval THUC SU "
                                        "da chay (khong chi de xuat).",
            "host_impact_evidence": "State-diff the hien anh huong len filesystem/process/"
                                     "network do thuc thi gay ra.",
        },
    ),
    AttackTypeDefinition(
        "ASI06", "memory_poisoning",
        {
            "persistence_channel": "Loai luu tru bi anh huong: summary, embedding, RAG store "
                                    "(khong bao gom prompt mot lan).",
            "seed_stage": "Du lieu doc duoc gieo vao dau, noi dung gieo la gi, qua kenh "
                          "ingest nao.",
            "trigger_stage": "Tuong tac SAU DO, noi agent tra cuu lai du lieu da bi gieo "
                              "va bi anh huong.",
        },
        {
            "seed_write_evidence": "Event the hien du lieu doc da duoc ghi vao memory/context "
                                    "o seed_stage.",
            "poisoned_retrieval_evidence": "Event the hien agent da doc lai dung du lieu doc "
                                            "o trigger_stage va bi anh huong quyet dinh.",
        },
    ),
    AttackTypeDefinition(
        "ASI07", "inter_agent_comm_compromise",
        {
            "comm_channel": "Kenh/giao thuc giao tiep giua agent (HTTP khong ma hoa, MCP, "
                             "A2A registry, message bus).",
            "manipulation_technique": "MITM injection / message tampering / replay / "
                                       "protocol downgrade / descriptor forgery / "
                                       "discovery routing attack.",
            "forged_content": "Noi dung message bi gia mao/sua doi/lam gia.",
        },
        {
            "message_integrity_violation_evidence": "Event the hien mot agent da hanh dong "
                                                      "theo message bi tampered/forged/replayed.",
            "downstream_effect_evidence": "Hanh dong ket qua xay ra do message bi tam thoa hiep.",
        },
    ),
    AttackTypeDefinition(
        "ASI08", "cascading_failure",
        {
            "origin_fault_reference": "Tham chieu ve loi goc (tu ASI04/06/07) da khoi phat "
                                       "chuoi loi.",
            "propagation_path": "planner-executor coupling, inter-agent cascade, "
                                 "auto-deployment cascade, feedback loop.",
            "fanout_scope": "Pham vi lan truyen ky vong: so agent/session/tenant bi anh huong.",
        },
        {
            "fanout_evidence": "Chuoi event tren nhieu agent/session the hien loi bi khuech "
                                "dai lap lai.",
            "systemic_impact_evidence": "State-diff the hien anh huong vuot ra ngoai pham vi "
                                         "loi goc.",
        },
    ),
    AttackTypeDefinition(
        "ASI09", "human_trust_exploitation",
        {
            "trust_exploit_technique": "insufficient_explainability / emotional_manipulation / "
                                        "fake_explainability.",
            "deceptive_output": "Ly le/noi dung thuyet phuc gia agent tao ra de dat duoc su "
                                 "chap thuan.",
            "human_decision_point": "Hanh dong/phe duyet cu the ma con nguoi bi dan dat "
                                     "thuc hien.",
        },
        {
            "human_approval_evidence": "Event the hien con nguoi da phe duyet/hanh dong dua "
                                        "theo noi dung gia ma khong xac minh doc lap.",
            "harmful_outcome_evidence": "State-diff the hien hanh dong gay hai da xay ra sau "
                                         "phe duyet.",
        },
    ),
    AttackTypeDefinition(
        "ASI10", "rogue_behavior",
        {
            "divergence_pattern": "goal_drift_scheming / workflow_hijacking / "
                                   "collusion_self_replication / reward_hacking.",
            "persistence_mechanism": "Cach hanh vi lech tiep dien sau khi nguon kich hoat "
                                      "ban dau da mat (vd: tiep tuc sau khi nguon doc hai bi "
                                      "go bo).",
            "affected_scope": "Cac workflow/agent bi anh huong boi su lech huong nay.",
        },
        {
            "behavioral_deviation_evidence": "Chuoi event qua nhieu tuong tac the hien lech "
                                              "khoi baseline hanh vi (khong phai 1 event don le).",
            "containment_failure_evidence": "Bang chung tung hanh dong rieng le co ve hop le, "
                                             "chi phat hien duoc khi xet tong the.",
        },
    ),
)

_INDEX: Dict[str, AttackTypeDefinition] = {d.asi_id: d for d in _FRAMEWORK}


def get_definition(asi_id: str) -> Optional[AttackTypeDefinition]:
    """Tra ve AttackTypeDefinition day du cho mot asi_id, hoac None neu chua co."""
    return _INDEX.get(asi_id.upper())


def get_attack_type(asi_id: str) -> str:
    """
    Tra ve nhan attack_type ung voi asi_id - day la buoc TU DONG khoa khung,
    khong cho nguoi tao TestSpec tu chon khung khac.
    """
    d = get_definition(asi_id)
    if d is None:
        raise KeyError(f"Chua co dinh nghia attack_type cho ma {asi_id.upper()}.")
    return d.attack_type


def required_mechanism_fields(asi_id: str) -> Tuple[str, ...]:
    d = get_definition(asi_id)
    if d is None:
        raise KeyError(f"Chua co dinh nghia attack_type cho ma {asi_id.upper()}.")
    return tuple(d.mechanism_fields.keys())


def required_evidence_fields(asi_id: str) -> Tuple[str, ...]:
    d = get_definition(asi_id)
    if d is None:
        raise KeyError(f"Chua co dinh nghia attack_type cho ma {asi_id.upper()}.")
    return tuple(d.evidence_fields.keys())


def list_all() -> Tuple[AttackTypeDefinition, ...]:
    """Tra ve toan bo 10 dinh nghia - dung de kiem tra du 10 ma da co khung."""
    return _FRAMEWORK


if __name__ == "__main__":
    all_defs = list_all()
    print(f"Tong so dinh nghia attack_type da nap: {len(all_defs)}")
    for d in all_defs:
        print(f"{d.asi_id} -> {d.attack_type} "
              f"(mechanism: {len(d.mechanism_fields)} field, "
              f"evidence: {len(d.evidence_fields)} field)")
