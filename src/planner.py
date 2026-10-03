"""Bộ lập kế hoạch tổng quát: Dijkstra trên trạng thái (ô, hướng, pha).

pha 0 = chưa ghé điểm via, pha 1 = đã ghé (hoặc không có via).
Chi phí một bước = chi phí cạnh theo trạng thái đường + chi phí rẽ so với hướng trước đó.
"""
import heapq
import math

from scene_graph import turn_kind

EPS = 1e-6


def resolve_targets(g, kind, ref):
    """Danh sách ô ứng viên cho một loại địa điểm (tham chiếu không gian chỉ rõ thì chỉ còn 1 ô)."""
    if kind is None:
        return None
    if ref is not None:
        return [tuple(ref["rc"])]
    return list(g.landmarks.get(kind, []))


def targets(g):
    m = g.mission
    goal = resolve_targets(g, m["goal"], m["goal_ref"])
    via = resolve_targets(g, m["via"], m["via_ref"])
    return goal, via


def step_cost(params, status, stairs, h_prev, h_new, oneway=False):
    c = params["edge"][status]
    if oneway:
        c += params.get("oneway_cost", 0.0)
    if stairs:
        c += params.get("stairs_cost", 0.0)
    if h_prev is not None:
        c += params["turn"][turn_kind(h_prev, h_new)]
    return c


def action_costs(g, params):
    """Trả về {action: tổng chi phí tối ưu nếu bước đầu là action}."""
    goal, via = targets(g)
    goal_set = set(goal)
    via_set = set(via) if via else None
    legged = params.get("legged", False)
    first_turn = params.get("first_turn", True)

    def phase_at(node, phase):
        if phase == 0 and node in via_set:
            return 1
        return phase

    def done(node, phase):
        return phase == 1 and node in goal_set

    start_phase = 0 if via_set else 1
    start_phase = phase_at(g.start, start_phase) if via_set else 1

    # Dijkstra ngược thì phức tạp vì chi phí rẽ; chạy xuôi từ từng bước đầu.
    out = {}
    for act, v, status, stairs in g.adj[g.start]:
        if stairs and not legged:
            continue
        c0 = step_cost(params, status, stairs, g.heading if first_turn else None, act,
                       (g.start, v) in g.oneway)
        st = (v, act, phase_at(v, start_phase))
        best = dijkstra(g, params, st, c0, phase_at, done, legged)
        if best < math.inf:
            out[act] = best
    return out


def dijkstra(g, params, st, c0, phase_at, done, legged):
    dist = {st: c0}
    pq = [(c0, st)]
    while pq:
        d, (u, h, ph) = heapq.heappop(pq)
        if d > dist[(u, h, ph)] + EPS:
            continue
        if done(u, ph):
            return d
        for act, v, status, stairs in g.adj[u]:
            if stairs and not legged:
                continue
            nd = d + step_cost(params, status, stairs, h, act, (u, v) in g.oneway)
            ns = (v, act, phase_at(v, ph))
            if nd < dist.get(ns, math.inf) - EPS:
                dist[ns] = nd
                heapq.heappush(pq, (nd, ns))
    return math.inf


def optimal_actions(costs):
    if not costs:
        return []
    m = min(costs.values())
    return sorted(a for a, c in costs.items() if c <= m + EPS)
