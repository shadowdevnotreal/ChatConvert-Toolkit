"""
Network Graph Analyzer - Visualizes conversation networks.

Creates interactive network graphs showing:
- Who talks to whom
- Message flow patterns
- Communication clustering
- Group dynamics

Uses networkx for graph structure and plotly for visualization.
"""

from typing import Dict, Any, List, Tuple, Optional
from collections import defaultdict, Counter
import logging

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

from .base_analyzer import BaseAnalyzer
from ..models import Conversation


class NetworkGraphAnalyzer(BaseAnalyzer):
    """
    Analyze conversation networks and create interactive visualizations.

    Requires networkx and plotly to be installed.
    """

    def __init__(self):
        """Initialize network graph analyzer."""
        super().__init__()
        self.logger = logging.getLogger(__name__)

        if not HAS_NETWORKX:
            self.logger.warning("networkx not installed. Network analysis unavailable.")
        if not HAS_PLOTLY:
            self.logger.warning("plotly not installed. Graph visualization unavailable.")

    def analyze(self, conversation: Conversation) -> Dict[str, Any]:
        """
        Analyze conversation network and create graph.

        Args:
            conversation: Conversation to analyze

        Returns:
            Dict with network analysis:
            {
                'graph_data': Dict (for plotly),
                'network_stats': Dict,
                'edges': List[Dict],
                'nodes': List[Dict],
                'available': bool
            }
        """
        if not HAS_NETWORKX or not HAS_PLOTLY:
            return {
                'available': False,
                'error': 'networkx or plotly not installed'
            }

        self._validate_conversation(conversation)

        # Build network graph
        G = self._build_network_graph(conversation)

        # Calculate network statistics
        network_stats = self._calculate_network_stats(G, conversation)

        # Create visualization data
        graph_data = self._create_plotly_graph(G, conversation)

        # Get edge and node details
        edges = self._get_edge_details(G)
        nodes = self._get_node_details(G)

        return {
            'available': True,
            'graph_data': graph_data,
            'network_stats': network_stats,
            'edges': edges,
            'nodes': nodes,
            'graph_object': G  # For further analysis if needed
        }

    def _build_network_graph(self, conversation: Conversation) -> 'nx.DiGraph':
        """Build directed network graph from conversation."""
        G = nx.DiGraph()

        # Add all participants as nodes
        participants = conversation.get_participants_list()
        for participant in participants:
            G.add_node(participant)

        # Count interactions (who responds to whom)
        messages = sorted(conversation.messages, key=lambda m: m.timestamp)

        # Build edges based on message sequences
        for i in range(1, len(messages)):
            prev_sender = messages[i-1].sender
            curr_sender = messages[i].sender

            # Add edge if different senders (response pattern)
            if prev_sender != curr_sender:
                if G.has_edge(curr_sender, prev_sender):
                    G[curr_sender][prev_sender]['weight'] += 1
                else:
                    G.add_edge(curr_sender, prev_sender, weight=1)

        return G

    def _calculate_network_stats(self, G: 'nx.DiGraph', conversation: Conversation) -> Dict[str, Any]:
        """Calculate network statistics."""
        stats = {}

        # Basic stats
        stats['total_nodes'] = G.number_of_nodes()
        stats['total_edges'] = G.number_of_edges()
        stats['is_connected'] = nx.is_weakly_connected(G)

        # Density (how interconnected)
        if G.number_of_nodes() > 1:
            stats['density'] = nx.density(G)
        else:
            stats['density'] = 0

        # Centrality measures (who is most central)
        if G.number_of_nodes() > 0:
            # Degree centrality (most connections)
            degree_centrality = nx.degree_centrality(G)
            stats['most_central'] = max(degree_centrality, key=degree_centrality.get) if degree_centrality else None
            stats['degree_centrality'] = degree_centrality

            # In-degree (most responded to)
            in_degree = dict(G.in_degree())
            stats['most_responded_to'] = max(in_degree, key=in_degree.get) if in_degree else None

            # Out-degree (responds most to others)
            out_degree = dict(G.out_degree())
            stats['most_responsive'] = max(out_degree, key=out_degree.get) if out_degree else None

        # Community detection (if applicable)
        if G.number_of_nodes() > 2:
            try:
                # Convert to undirected for community detection
                G_undirected = G.to_undirected()
                communities = nx.community.greedy_modularity_communities(G_undirected)
                stats['num_communities'] = len(communities)
                stats['communities'] = [list(community) for community in communities]
            except:
                stats['num_communities'] = 1
                stats['communities'] = [list(G.nodes())]
        else:
            stats['num_communities'] = 1
            stats['communities'] = [list(G.nodes())]

        return stats

    def _create_plotly_graph(self, G: 'nx.DiGraph', conversation: Conversation) -> Dict[str, Any]:
        """Create plotly graph visualization data."""
        # Use spring layout for node positions
        try:
            pos = nx.spring_layout(G, k=0.5, iterations=50)
        except:
            pos = nx.circular_layout(G)

        # Create edge traces
        edge_traces = []

        for edge in G.edges(data=True):
            source, target, data = edge
            weight = data.get('weight', 1)

            x0, y0 = pos[source]
            x1, y1 = pos[target]

            # Create edge trace
            edge_trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(
                    width=min(weight / 2, 10),  # Scale line width by weight
                    color='rgba(125, 125, 125, 0.5)'
                ),
                hoverinfo='text',
                text=f'{source} → {target}: {weight} responses',
                showlegend=False
            )
            edge_traces.append(edge_trace)

        # Create node trace
        node_x = []
        node_y = []
        node_text = []
        node_size = []
        node_color = []

        # Count messages per participant
        message_counts = Counter(msg.sender for msg in conversation.messages)

        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

            # Node info
            msg_count = message_counts.get(node, 0)
            in_degree = G.in_degree(node)
            out_degree = G.out_degree(node)

            node_text.append(
                f'<b>{node}</b><br>'
                f'Messages: {msg_count}<br>'
                f'Responses to others: {out_degree}<br>'
                f'Responded to by others: {in_degree}'
            )

            # Size based on message count
            node_size.append(max(20, min(msg_count * 2, 80)))

            # Color based on total degree
            total_degree = in_degree + out_degree
            node_color.append(total_degree)

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=[node for node in G.nodes()],
            textposition='top center',
            hovertext=node_text,
            marker=dict(
                size=node_size,
                color=node_color,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(
                    title='Total Connections',
                    thickness=15,
                    len=0.7
                ),
                line=dict(width=2, color='white')
            ),
            showlegend=False
        )

        # Create figure
        fig = go.Figure(
            data=edge_traces + [node_trace],
            layout=go.Layout(
                title=dict(
                    text=f'Conversation Network: {conversation.title}',
                    x=0.5,
                    xanchor='center'
                ),
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=600
            )
        )

        # Return figure JSON for streamlit
        return fig.to_dict()

    def _get_edge_details(self, G: 'nx.DiGraph') -> List[Dict[str, Any]]:
        """Get detailed edge information."""
        edges = []

        for source, target, data in G.edges(data=True):
            edges.append({
                'from': source,
                'to': target,
                'weight': data.get('weight', 1),
                'description': f'{source} responded to {target} {data.get("weight", 1)} times'
            })

        # Sort by weight (strongest connections first)
        edges.sort(key=lambda x: x['weight'], reverse=True)

        return edges

    def _get_node_details(self, G: 'nx.DiGraph') -> List[Dict[str, Any]]:
        """Get detailed node information."""
        nodes = []

        # Calculate centrality
        degree_centrality = nx.degree_centrality(G) if G.number_of_nodes() > 0 else {}

        for node in G.nodes():
            in_degree = G.in_degree(node)
            out_degree = G.out_degree(node)

            nodes.append({
                'name': node,
                'in_degree': in_degree,
                'out_degree': out_degree,
                'total_degree': in_degree + out_degree,
                'centrality': degree_centrality.get(node, 0),
                'description': f'{node}: {in_degree} incoming, {out_degree} outgoing connections'
            })

        # Sort by total degree (most connected first)
        nodes.sort(key=lambda x: x['total_degree'], reverse=True)

        return nodes

    def generate_report(self, conversation: Conversation) -> str:
        """Generate text report of network analysis."""
        results = self.analyze(conversation)

        if not results.get('available'):
            return "Network analysis not available (requires networkx and plotly)"

        report = []
        report.append("="*60)
        report.append("NETWORK ANALYSIS REPORT")
        report.append("="*60)
        report.append("")

        stats = results['network_stats']

        # Network overview
        report.append("NETWORK OVERVIEW")
        report.append("-"*60)
        report.append(f"Participants: {stats['total_nodes']}")
        report.append(f"Connections: {stats['total_edges']}")
        report.append(f"Network Density: {stats.get('density', 0):.2%}")
        report.append(f"Connected: {'Yes' if stats.get('is_connected') else 'No'}")
        report.append("")

        # Key participants
        report.append("KEY PARTICIPANTS")
        report.append("-"*60)
        if stats.get('most_central'):
            report.append(f"Most Central: {stats['most_central']}")
        if stats.get('most_responded_to'):
            report.append(f"Most Responded To: {stats['most_responded_to']}")
        if stats.get('most_responsive'):
            report.append(f"Most Responsive: {stats['most_responsive']}")
        report.append("")

        # Top connections
        report.append("TOP CONNECTIONS")
        report.append("-"*60)
        edges = results['edges'][:5]
        for i, edge in enumerate(edges, 1):
            report.append(f"{i}. {edge['description']}")
        report.append("")

        # Communities
        if stats.get('num_communities', 1) > 1:
            report.append("COMMUNITIES")
            report.append("-"*60)
            report.append(f"Detected {stats['num_communities']} communication groups")
            for i, community in enumerate(stats.get('communities', []), 1):
                members = ', '.join(community)
                report.append(f"  Group {i}: {members}")
            report.append("")

        report.append("="*60)

        return "\n".join(report)
