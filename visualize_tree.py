"""
Game Tree Visualization - HTML Output
======================================
Generates an interactive HTML page for viewing
the game tree without requiring graphviz installation.
"""

from game import generate_tree, finalize_score, determine_winner
import json
import webbrowser
import os


def tree_to_dict(node):
    """Converts a GameNode tree into a JSON-compatible dict structure."""
    d = {
        "number": node.number,
        "points": node.points,
        "bank": node.bank,
        "player": node.player,
        "depth": node.depth,
        "move": node.move,
        "terminal": node.terminal,
        "winner": node.winner,
        "children": [tree_to_dict(c) for c in node.children],
    }
    return d


def generate_html(tree_data, start_number, max_depth):
    """Generates an HTML visualization page from the tree data."""
    tree_json = json.dumps(tree_data, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Game Tree - N={start_number}, Depth={max_depth}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1a1a2e;
            color: #eee;
            overflow: auto;
        }}
        .header {{
            background: linear-gradient(135deg, #16213e, #0f3460);
            padding: 18px 30px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.4);
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .header h1 {{
            font-size: 22px;
            color: #e94560;
            margin-bottom: 6px;
        }}
        .header p {{
            font-size: 13px;
            color: #aaa;
        }}
        .legend {{
            display: flex;
            justify-content: center;
            gap: 24px;
            margin-top: 10px;
            flex-wrap: wrap;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
        }}
        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 3px;
            border: 1px solid rgba(255,255,255,0.2);
        }}
        .controls {{
            display: flex;
            justify-content: center;
            gap: 12px;
            margin-top: 12px;
        }}
        .controls button {{
            padding: 6px 16px;
            border: 1px solid #e94560;
            background: transparent;
            color: #e94560;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.2s;
        }}
        .controls button:hover {{
            background: #e94560;
            color: #fff;
        }}
        #tree-container {{
            padding: 40px 20px;
            overflow: auto;
            min-height: calc(100vh - 130px);
        }}
        svg {{
            display: block;
            margin: 0 auto;
        }}
        .node-group {{
            cursor: pointer;
        }}
        .node-rect {{
            rx: 6;
            ry: 6;
            stroke-width: 2;
            transition: all 0.2s;
        }}
        .node-group:hover .node-rect {{
            filter: brightness(1.2);
            stroke-width: 3;
        }}
        .node-text {{
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 11px;
            fill: #222;
            pointer-events: none;
        }}
        .edge-line {{
            stroke: #556;
            stroke-width: 1.5;
            fill: none;
        }}
        .edge-label {{
            font-family: 'Segoe UI', sans-serif;
            font-size: 10px;
            fill: #e94560;
            font-weight: bold;
        }}
        .tooltip {{
            position: fixed;
            background: #16213e;
            border: 1px solid #e94560;
            border-radius: 6px;
            padding: 10px 14px;
            font-size: 12px;
            color: #eee;
            pointer-events: none;
            z-index: 200;
            display: none;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        }}
        .tooltip .tt-row {{
            margin: 3px 0;
        }}
        .tooltip .tt-label {{
            color: #e94560;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Game Tree Visualization</h1>
        <p>Start number: <strong>{start_number}</strong> | Depth limit: <strong>{max_depth}</strong></p>
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background: #4CAF50;"></div>
                <span>Computer Wins (P1)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #42A5F5;"></div>
                <span>Human Wins (P2)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #fff;"></div>
                <span>Intermediate Node</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #FFB74D;"></div>
                <span>Leaf (Heuristic)</span>
            </div>
        </div>
        <div class="controls">
            <button onclick="zoomIn()">Zoom In</button>
            <button onclick="zoomOut()">Zoom Out</button>
            <button onclick="resetZoom()">Reset</button>
        </div>
    </div>
    <div id="tree-container"></div>
    <div class="tooltip" id="tooltip"></div>

    <script>
    const treeData = {tree_json};

    // --------------- LAYOUT CALCULATION ---------------
    const NODE_W = 100;
    const NODE_H = 62;
    const H_GAP = 16;
    const V_GAP = 60;

    let currentScale = 1;

    // Assign position (x, y) to each node
    function layoutTree(node, depth) {{
        node._depth = depth;

        if (!node.children || node.children.length === 0) {{
            node._width = NODE_W;
            return;
        }}

        node.children.forEach(c => layoutTree(c, depth + 1));

        let totalChildWidth = 0;
        node.children.forEach(c => {{ totalChildWidth += c._width; }});
        totalChildWidth += (node.children.length - 1) * H_GAP;

        node._width = Math.max(NODE_W, totalChildWidth);
    }}

    function positionTree(node, x, y) {{
        node._x = x + node._width / 2 - NODE_W / 2;
        node._y = y;

        if (!node.children || node.children.length === 0) return;

        let totalChildWidth = 0;
        node.children.forEach(c => {{ totalChildWidth += c._width; }});
        totalChildWidth += (node.children.length - 1) * H_GAP;

        let startX = x + node._width / 2 - totalChildWidth / 2;

        node.children.forEach(c => {{
            positionTree(c, startX, y + NODE_H + V_GAP);
            startX += c._width + H_GAP;
        }});
    }}

    function getMaxXY(node) {{
        let maxX = node._x + NODE_W;
        let maxY = node._y + NODE_H;
        if (node.children) {{
            node.children.forEach(c => {{
                const [mx, my] = getMaxXY(c);
                maxX = Math.max(maxX, mx);
                maxY = Math.max(maxY, my);
            }});
        }}
        return [maxX, maxY];
    }}

    layoutTree(treeData, 0);
    positionTree(treeData, 0, 0);
    const [maxX, maxY] = getMaxXY(treeData);
    const svgW = maxX + 40;
    const svgH = maxY + 40;

    // --------------- SVG RENDERING ---------------
    function getNodeColor(n) {{
        if (n.terminal) {{
            return n.winner === 1 ? '#4CAF50' : '#42A5F5';
        }}
        if (!n.children || n.children.length === 0) {{
            return '#FFB74D'; // leaf node (heuristic)
        }}
        return '#ffffff';
    }}

    function getNodeStroke(n) {{
        if (n.terminal) {{
            return n.winner === 1 ? '#2E7D32' : '#1565C0';
        }}
        if (!n.children || n.children.length === 0) {{
            return '#E65100';
        }}
        return '#999';
    }}

    let svgContent = '';

    // Draw edges first (behind nodes)
    function drawEdges(node) {{
        if (!node.children) return;
        node.children.forEach(child => {{
            const x1 = node._x + NODE_W / 2 + 20;
            const y1 = node._y + NODE_H;
            const x2 = child._x + NODE_W / 2 + 20;
            const y2 = child._y;
            const midY = (y1 + y2) / 2;

            svgContent += `<path class="edge-line" d="M${{x1}},${{y1}} C${{x1}},${{midY}} ${{x2}},${{midY}} ${{x2}},${{y2}}" />`;

            // Edge label (divisor)
            if (child.move) {{
                const labelX = (x1 + x2) / 2;
                const labelY = midY - 4;
                svgContent += `<text class="edge-label" x="${{labelX}}" y="${{labelY}}" text-anchor="middle">/${{child.move}}</text>`;
            }}

            drawEdges(child);
        }});
    }}

    function drawNodes(node) {{
        const x = node._x + 20;
        const y = node._y + 20;
        const fill = getNodeColor(node);
        const stroke = getNodeStroke(node);

        const playerLabel = node.player === 1 ? 'PC' : 'Human';

        let lines = [
            `N=${{node.number}}`,
            `P=${{node.points}}  B=${{node.bank}}`,
            `Pl=${{node.player}} (${{playerLabel}})`
        ];

        if (node.terminal) {{
            lines.push(`Winner: P${{node.winner}}`);
        }}

        svgContent += `<g class="node-group" data-info='${{JSON.stringify(node).replace(/'/g, "&apos;")}}' onmouseenter="showTip(event, this)" onmouseleave="hideTip()">`;
        svgContent += `<rect class="node-rect" x="${{x}}" y="${{y}}" width="${{NODE_W}}" height="${{NODE_H}}" fill="${{fill}}" stroke="${{stroke}}" />`;

        lines.forEach((line, i) => {{
            svgContent += `<text class="node-text" x="${{x + NODE_W/2}}" y="${{y + 15 + i * 14}}" text-anchor="middle">${{line}}</text>`;
        }});

        svgContent += `</g>`;

        if (node.children) {{
            node.children.forEach(c => drawNodes(c));
        }}
    }}

    drawEdges(treeData);
    drawNodes(treeData);

    const container = document.getElementById('tree-container');
    container.innerHTML = `<svg id="tree-svg" width="${{svgW + 40}}" height="${{svgH + 40}}" viewBox="0 0 ${{svgW + 40}} ${{svgH + 40}}">${{svgContent}}</svg>`;

    // --------------- ZOOM ---------------
    function zoomIn() {{
        currentScale *= 1.2;
        applySvgScale();
    }}
    function zoomOut() {{
        currentScale /= 1.2;
        applySvgScale();
    }}
    function resetZoom() {{
        currentScale = 1;
        applySvgScale();
    }}
    function applySvgScale() {{
        const svg = document.getElementById('tree-svg');
        svg.style.transform = `scale(${{currentScale}})`;
        svg.style.transformOrigin = 'top center';
    }}

    // --------------- TOOLTIP ---------------
    function showTip(event, el) {{
        const data = JSON.parse(el.getAttribute('data-info'));
        const tip = document.getElementById('tooltip');
        const playerName = data.player === 1 ? 'Computer' : 'Human';
        let html = `
            <div class="tt-row"><span class="tt-label">Number:</span> ${{data.number}}</div>
            <div class="tt-row"><span class="tt-label">Points:</span> ${{data.points}}</div>
            <div class="tt-row"><span class="tt-label">Bank:</span> ${{data.bank}}</div>
            <div class="tt-row"><span class="tt-label">Player:</span> ${{data.player}} (${{playerName}})</div>
            <div class="tt-row"><span class="tt-label">Depth:</span> ${{data.depth}}</div>
        `;
        if (data.move) {{
            html += `<div class="tt-row"><span class="tt-label">Move:</span> /${{data.move}}</div>`;
        }}
        if (data.terminal) {{
            const winnerName = data.winner === 1 ? 'Computer' : 'Human';
            html += `<div class="tt-row"><span class="tt-label">Winner:</span> P${{data.winner}} (${{winnerName}})</div>`;
        }}
        tip.innerHTML = html;
        tip.style.display = 'block';
        tip.style.left = (event.clientX + 15) + 'px';
        tip.style.top = (event.clientY + 15) + 'px';
    }}

    function hideTip() {{
        document.getElementById('tooltip').style.display = 'none';
    }}

    document.addEventListener('mousemove', e => {{
        const tip = document.getElementById('tooltip');
        if (tip.style.display === 'block') {{
            tip.style.left = (e.clientX + 15) + 'px';
            tip.style.top = (e.clientY + 15) + 'px';
        }}
    }});
    </script>
</body>
</html>"""
    return html


def main():
    """Main function: builds the tree and saves it as HTML."""
    start_number = 120
    max_depth = 6

    print(f"Building tree... (N={start_number}, depth={max_depth})")
    tree = generate_tree(start_number, max_depth=max_depth)

    print("Converting to JSON...")
    tree_data = tree_to_dict(tree)

    print("Generating HTML...")
    html = generate_html(tree_data, start_number, max_depth)

    output_path = os.path.join(os.path.dirname(__file__), "game_tree.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nTree saved to: {output_path}")
    print("Opening in browser...")
    webbrowser.open(f"file:///{output_path.replace(os.sep, '/')}")


if __name__ == "__main__":
    main()
