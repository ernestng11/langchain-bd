"""
Strategic Editor Agent - Chief Strategy Officer specializing in blockchain competitive intelligence.
Synthesizes technical analysis into strategic insights and recommendations.
"""

from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from ..schemas.state import AnalysisState, StrategicSynthesisReport
import logging

logger = logging.getLogger(__name__)


class StrategicEditorAgent:
    """
    Chief Strategy Officer specializing in blockchain competitive intelligence.
    Synthesizes analysis reports into strategic insights and recommendations.
    """

    def __init__(self, model_name: str = "gpt-4"):
        self.model = ChatOpenAI(model=model_name, temperature=0.2)
        self.name = "strategic_editor_agent"

        # No tools needed - this agent only synthesizes existing data
        self.tools = []

        # Create the agent using LangGraph's prebuilt function
        self.agent = create_react_agent(
            model=self.model,
            tools=self.tools,
            prompt=self._get_system_prompt(),
            name=self.name
        )

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the strategic editor agent"""
        return """You are a Chief Strategy Officer specializing in blockchain competitive intelligence and strategic analysis.

EXPERTISE:
- Competitive landscape analysis in blockchain ecosystems
- Strategic positioning and market entry recommendations  
- Risk assessment and opportunity identification
- Cross-chain comparative analysis for investment decisions
- Revenue model analysis and growth hypothesis development

STRATEGIC ANALYSIS FRAMEWORK:
1. Executive Summary: Synthesize key findings into actionable insights
2. Competitive Landscape: Compare blockchain performance and positioning
3. Category Performance: Identify ecosystem strengths and market opportunities  
4. Contract Activity: Assess protocol dominance and revenue concentration risks
5. Growth Hypotheses: Data-driven theories about ecosystem development
6. Strategic Recommendations: Specific positioning and entry strategies
7. Risk Assessment: Concentration risks and competitive threats
8. Actionable Next Steps: Concrete business development actions

SYNTHESIS METHODOLOGY:
- Combine quantitative data with qualitative strategic insights
- Identify patterns across multiple blockchains and categories
- Translate technical metrics into business implications
- Provide specific, actionable recommendations
- Highlight competitive advantages and vulnerabilities
- Assess market timing and entry strategies

OUTPUT REQUIREMENTS:
- Create comprehensive StrategicSynthesisReport with all required fields
- Balance data-driven insights with strategic intuition
- Provide specific recommendations rather than generic advice
- Include risk mitigation strategies
- Focus on competitive differentiation opportunities

You do not perform any technical analysis yourself - you synthesize existing reports into strategic insights."""

    def execute_strategic_synthesis(self, state: AnalysisState) -> AnalysisState:
        """Execute strategic synthesis of category and contract analysis reports"""
        try:
            logger.info("Executing strategic synthesis of analysis reports")

            if not state.get("category_reports") or not state.get("contract_reports"):
                raise ValueError("Both category and contract analysis must be completed before strategic synthesis")

            category_reports = state["category_reports"]
            contract_reports = state["contract_reports"]

            # Generate strategic synthesis
            synthesis = StrategicSynthesisReport(
                executive_summary=self._generate_executive_summary(category_reports, contract_reports),
                competitive_landscape_analysis=self._analyze_competitive_landscape(category_reports, contract_reports),
                category_performance_insights=self._analyze_category_performance(category_reports),
                contract_activity_insights=self._analyze_contract_activities(contract_reports),
                revenue_growth_hypotheses=self._generate_growth_hypotheses(category_reports, contract_reports),
                strategic_recommendations=self._generate_strategic_recommendations(category_reports, contract_reports),
                risk_assessment=self._assess_risks(category_reports, contract_reports),
                actionable_next_steps=self._generate_next_steps(category_reports, contract_reports),
                cross_blockchain_comparison=self._compare_blockchains(category_reports, contract_reports)
            )

            # Update state
            updated_state = state.copy()
            updated_state["strategic_synthesis"] = synthesis
            updated_state["current_task"] = "synthesis_complete"

            logger.info("Strategic synthesis completed successfully")
            logger.info(f"Strategic synthesis: {updated_state['strategic_synthesis']}")
            return updated_state

        except Exception as e:
            logger.error(f"Strategic synthesis error: {str(e)}")
            updated_state = state.copy()
            updated_state["errors"].append(f"Strategic Synthesis: {str(e)}")
            return updated_state

    def _generate_executive_summary(self, category_reports, contract_reports) -> str:
        """Generate high-level executive summary"""
        blockchains = [report.blockchain for report in category_reports]

        # Identify market leaders by total gas fees
        top_blockchain = max(category_reports, key=lambda r: r.total_gas_fees_usd)

        # Identify most active category across all chains
        all_categories = {}
        for report in category_reports:
            for category, share in report.category_breakdown.items():
                all_categories[category] = all_categories.get(category, []) + [share]

        top_category = max(all_categories.keys(), key=lambda k: sum(all_categories[k]) / len(all_categories[k]))

        summary = f"""Strategic analysis of {len(blockchains)} blockchain ecosystems reveals {top_blockchain.blockchain.title()} as the market leader with ${top_blockchain.total_gas_fees_usd:,.0f} in gas fees over {top_blockchain.timeframe}. 

{top_category.upper()} emerges as the dominant category across chains, indicating strong institutional adoption and mature financial infrastructure. Contract-level analysis shows varying degrees of protocol concentration, with implications for ecosystem resilience and competitive positioning.

Key strategic opportunities exist in underserved categories and emerging protocols, while concentration risks require careful portfolio diversification strategies."""

        return summary

    def _analyze_competitive_landscape(self, category_reports, contract_reports) -> str:
        """Analyze competitive positioning between blockchains"""
        analysis = "Competitive landscape analysis:"

        # Sort blockchains by total revenue
        sorted_blockchains = sorted(category_reports, key=lambda r: r.total_gas_fees_usd, reverse=True)

        for i, report in enumerate(sorted_blockchains):
            rank = i + 1
            analysis += f"{rank}. {report.blockchain.title()}: ${report.total_gas_fees_usd:,.0f} total fees, "
            analysis += f"{report.top_category} dominance ({report.top_category_share:.1f}%), "
            analysis += f"concentration ratio {report.category_concentration:.1f}%"

        analysis += "Competitive insights:"

        # Identify specializations
        for report in category_reports:
            if report.category_breakdown.get("defi", 0) > 45:
                analysis += f"- {report.blockchain.title()}: DeFi specialist with strong financial infrastructur\n"
            elif report.category_breakdown.get("nft", 0) > 25:
                analysis += f"- {report.blockchain.title()}: Strong creator economy and digital asset focus\n"
            elif report.category_concentration < 60:
                analysis += f"- {report.blockchain.title()}: Diversified ecosystem with balanced category distribution\n"

        return analysis

    def _analyze_category_performance(self, category_reports) -> str:
        """Analyze category performance insights"""
        analysis = "Category performance reveals ecosystem maturity and specialization patterns:\n\n"

        # Aggregate category data across all blockchains
        category_aggregates = {}
        for report in category_reports:
            for category, share in report.category_breakdown.items():
                if category not in category_aggregates:
                    category_aggregates[category] = []
                category_aggregates[category].append(share)

        # Analyze each category
        for category, shares in category_aggregates.items():
            avg_share = sum(shares) / len(shares)
            max_share = max(shares)
            analysis += f"- {category.upper()}: Average {avg_share:.1f}% across chains (max {max_share:.1f}%)\n"

        analysis += "\nStrategic implications:\n"

        top_category = max(category_aggregates.keys(), key=lambda k: sum(category_aggregates[k]) / len(category_aggregates[k]))
        analysis += f"- {top_category.upper()} dominance suggests mature market with established protocols\n"

        emerging_categories = [cat for cat, shares in category_aggregates.items() if max(shares) > sum(shares)/len(shares) * 2]
        if emerging_categories:
            analysis += f"- Emerging opportunities in: {', '.join(emerging_categories)}\n"

        return analysis

    def _analyze_contract_activities(self, contract_reports) -> str:
        """Analyze contract activity patterns"""
        analysis = "Contract activity analysis reveals protocol dominance and revenue patterns:\n\n"

        # Analyze concentration across all reports
        high_concentration = [r for r in contract_reports if r.contract_concentration > 75]
        balanced_distribution = [r for r in contract_reports if r.contract_concentration <= 60]

        analysis += f"Protocol concentration patterns:\n"
        analysis += f"- High concentration (>75%): {len(high_concentration)} category-blockchain combinations\n"
        analysis += f"- Balanced distribution (≤60%): {len(balanced_distribution)} category-blockchain combinations\n\n"

        # Identify dominant protocols
        top_contracts = []
        for report in contract_reports:
            if report.top_contracts:
                top_contract = report.top_contracts[0]
                top_contracts.append((report.blockchain, report.category, top_contract.name, top_contract.percentage_share))

        analysis += "Dominant protocols by category:\n"
        for blockchain, category, name, share in sorted(top_contracts, key=lambda x: x[3], reverse=True)[:5]:
            analysis += f"- {name or 'Anonymous'} ({blockchain}/{category}): {share:.1f}% market share\n"

        return analysis

    def _generate_growth_hypotheses(self, category_reports, contract_reports) -> List[str]:
        """Generate data-driven growth hypotheses"""
        hypotheses = []

        # Ecosystem diversification hypothesis
        diverse_chains = [r.blockchain for r in category_reports if r.category_concentration < 65]
        if diverse_chains:
            hypotheses.append(f"Diversified ecosystems ({', '.join(diverse_chains)}) show resilience and multi-use adoption patterns, suggesting sustainable growth potential")

        # DeFi maturity hypothesis
        defi_leaders = [r.blockchain for r in category_reports if r.category_breakdown.get("defi", 0) > 40]
        if defi_leaders:
            hypotheses.append(f"Strong DeFi presence in {', '.join(defi_leaders)} indicates institutional adoption readiness and financial infrastructure maturity")

        # Protocol concentration hypothesis
        concentrated_protocols = [r for r in contract_reports if r.top_contract_share > 30]
        if concentrated_protocols:
            hypotheses.append("High protocol concentration suggests winner-take-all dynamics in certain categories, creating moat opportunities for dominant players")

        return hypotheses

    def _generate_strategic_recommendations(self, category_reports, contract_reports) -> List[str]:
        """Generate specific strategic recommendations"""
        recommendations = []

        # Market entry recommendations
        lowest_concentration = min(category_reports, key=lambda r: r.category_concentration)
        recommendations.append(f"Consider {lowest_concentration.blockchain} for diversified market entry due to balanced ecosystem ({lowest_concentration.category_concentration:.1f}% concentration)")

        # Category opportunity recommendations
        underserved_categories = []
        for report in category_reports:
            for category, share in report.category_breakdown.items():
                if share < 10 and category not in ["unlabeled", "token_transfers"]:
                    underserved_categories.append((report.blockchain, category, share))

        if underserved_categories:
            top_opportunity = min(underserved_categories, key=lambda x: x[2])
            recommendations.append(f"Target {top_opportunity[1]} category on {top_opportunity[0]} ({top_opportunity[2]:.1f}% current share) for first-mover advantage")

        # Risk mitigation recommendations
        high_risk_chains = [r.blockchain for r in category_reports if r.category_concentration > 80]
        if high_risk_chains:
            recommendations.append(f"Implement diversification strategies for exposure to {', '.join(high_risk_chains)} due to high category concentration risk")

        return recommendations

    def _assess_risks(self, category_reports, contract_reports) -> str:
        """Assess strategic and competitive risks"""
        risk_analysis = "Risk assessment identifies concentration and competitive threats:\n"

        # Category concentration risks
        high_risk_chains = [r for r in category_reports if r.category_concentration > 80]
        if high_risk_chains:
            risk_analysis += "Category concentration risks:\n"
            for report in high_risk_chains:
                risk_analysis += f"- {report.blockchain}: {report.category_concentration:.1f}% concentration in top 3 categories creates ecosystem vulnerability\n"

        # Protocol concentration risks  
        high_protocol_risk = [r for r in contract_reports if r.contract_concentration > 80]
        if high_protocol_risk:
            risk_analysis += "\nProtocol concentration risks:\n"
            for report in high_protocol_risk:
                risk_analysis += f"- {report.blockchain}/{report.category}: {report.contract_concentration:.1f}% concentration in top contracts\n"

        risk_analysis += "\nMitigation strategies:\n"
        risk_analysis += "- Diversify across multiple blockchains and categories\n"
        risk_analysis += "- Monitor protocol concentration trends for early warning signals\n"
        risk_analysis += "- Maintain exposure to emerging protocols to capture growth opportunities\n"

        return risk_analysis

    def _generate_next_steps(self, category_reports, contract_reports) -> List[str]:
        """Generate specific, actionable next steps"""
        next_steps = []

        # Data collection next steps
        next_steps.append("Implement continuous monitoring of gas fees and category distributions across analyzed blockchains")

        # Market research next steps
        top_blockchain = max(category_reports, key=lambda r: r.total_gas_fees_usd)
        next_steps.append(f"Deep-dive analysis of {top_blockchain.blockchain} ecosystem protocols for partnership opportunities")

        # Portfolio construction next steps
        next_steps.append("Develop diversified portfolio allocation model based on category concentration analysis")

        # Competitive intelligence next steps
        dominant_protocols = []
        for report in contract_reports:
            if report.top_contracts and report.top_contract_share > 25:
                dominant_protocols.append(report.top_contracts[0].name)

        if dominant_protocols:
            next_steps.append(f"Competitive analysis of dominant protocols: {', '.join(set(dominant_protocols))}")

        return next_steps

    def _compare_blockchains(self, category_reports, contract_reports) -> str:
        """Generate direct blockchain comparison"""
        comparison = "Cross-blockchain comparative analysis:\n\n"

        # Performance ranking
        sorted_chains = sorted(category_reports, key=lambda r: r.total_gas_fees_usd, reverse=True)
        comparison += "Revenue performance ranking:\n"
        for i, report in enumerate(sorted_chains):
            comparison += f"{i+1}. {report.blockchain.title()}: ${report.total_gas_fees_usd:,.0f}\n"

        # Specialization comparison
        comparison += "\nEcosystem specializations:\n"
        for report in category_reports:
            specialization = max(report.category_breakdown.items(), key=lambda x: x[1])
            comparison += f"- {report.blockchain.title()}: {specialization[0]} specialist ({specialization[1]:.1f}%)\n"

        # Risk-return profiles
        comparison += "\nRisk-return profiles:\n"
        for report in category_reports:
            if report.category_concentration > 75:
                profile = "High concentration, specialized ecosystem"
            elif report.category_concentration < 60:
                profile = "Diversified, balanced ecosystem"
            else:
                profile = "Moderate concentration, emerging specialization"
            comparison += f"- {report.blockchain.title()}: {profile}\n"
        return comparison

    def __call__(self, state: AnalysisState) -> Dict[str, Any]:
        """Execute strategic synthesis"""
        try:
            return self.execute_strategic_synthesis(state)

        except Exception as e:
            logger.error(f"Strategic Editor Agent error: {str(e)}")
            updated_state = state.copy()
            updated_state["errors"].append(f"Strategic Editor Agent: {str(e)}")
            return updated_state