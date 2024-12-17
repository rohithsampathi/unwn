# app/services/anthropic.py

import anthropic
from app.core.config import settings
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)

class AnthropicService:
    def __init__(self):
        self.client = anthropic.Client(api_key=settings.ANTHROPIC_API_KEY)

    async def get_elon_analysis(self, content: str) -> str:
        try:
            response = await anthropic.AsyncAnthropic().messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                temperature=0.2,
                messages=[{
                    "role": "user",
                    "content": f"""Analyze this content as a strategic business analyst focused on market implications, 
                    growth opportunities, and potential risks. Format the response in clear sections with numbered points.
                    
                    Content: {content}"""
                }]
            )
            # Handle the new response format
            text_content = response.content[0].text if isinstance(response.content, list) else str(response.content)
            return self._format_response(text_content)
        except Exception as e:
            logger.error(f"Error in elon analysis: {e}")
            raise

    async def get_jobs_analysis(self, content: str) -> str:
        try:
            logger.info(f"Getting jobs analysis for content")
            response = await anthropic.AsyncAnthropic().messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                temperature=0.2,
                messages=[{
                    "role": "user",
                    "content": f"""
                    **Objective:

                    Using your expertise as Marketer Jobs, delve into the provided market news story and  Knowledge Base data of key industries like Agri Tech, Animal Nutrition & Pet Care, Semiconductors, Aerospace, Automotive & EV, Health Tech & Medical Devices, and Food Tech  to synthesize a comprehensive understanding of the news story. Your task is to craft a LinkedIn business strategy story and a succinct, engaging tweet in response to the current news development. Your narrative should demonstrate deep market insights, leveraging cross-industry knowledge to propose timely, impactful strategies and implications.

                    For LinkedIn, create a post that encapsulates the essence of the news while highlighting its strategic significance, market impact, and potential investment opportunities. Your post should be professional, informative, and resonate with investors and business leaders. Use a tone that balances expertise with accessibility, avoiding overly complex jargon.

                    For Twitter, distill your insights into an engaging, concise abstract that piques interest and directs readers to further details.

                    Ensure your advice is ethically sound, compliant with financial advisory regulations, and tailored to the user's specific interests. 

                    Instructions:

                    1. Data Analysis: Examine the Knowledge Base, focusing on key metrics and trends across industries. Identify notable patterns, growth opportunities, and risks.
                    2. Business Insights: Articulate significant market trends and potential shifts in the industry landscape.
                    3. Investment Advice: Offer well-founded investment recommendations based on your analysis.
                    4. LinkedIn Post: Compose a professional, informative business strategy story. Include strategic significance, market impact, and investment opportunities.
                    5. Twitter Post: Craft a brief, engaging tweet that encapsulates key insights and encourages further reading.
                    6. Professional Tone: Ensure the communication style is expert, trustworthy, and accessible.
                    7.Clarity and Precision: Present analysis and recommendations with clear, precise language.
                    8. Tailored Responses: Align advice with the user's specific queries and interests.
                    9. Compliance and Ethics: Adhere to ethical standards and financial advisory regulations.
                    10. Limitations: Direct users to Market Unwinded's contact for queries beyond the provided analysis scope.
                    11. Remember to adhere to LinkedIn and Twitter character limits. Your goal is to create content that informs and influences the world's top investors and venture capital firms."

                    Example 1 - AgriTech News

                    #AgriTech Advancement: CENSANEXT & SAP's Strategic Union Nurtures Startups

                    The agri-tech and food value chain ecosystems stand on the brink of a revolution, as CENSANEXT, the tech subsidiary of WayCool Foods joins forces with SAP Labs India. This alliance is set to redefine the digital journey for startups, streamlining their path to technological empowerment and market dominion.

                    Strategic Insights:
                    🌱 Integration of SAP S/4HANA offers startups a scalable, enterprise-level ERP solution, democratizing access to cutting-edge technology.
                    🌱 CENSANEXT's management of shared infrastructure means startups face fewer barriers to operational excellence.
                    🌱 The collaboration crafts tailored growth pathways for these burgeoning entities, priming them for an escalating scale-up process.

                    Investor's Perspective:
                    💼 The CENSANEXT-SAP collaboration spells out a promising avenue for investments in agri-tech startups that embrace advanced ERP systems from their nascent stages.
                    💼 Startups utilizing these ERP systems are positioned to build sustainable competitive advantages, potentially leading to lucrative long-term investments.
                    💼 The ease of ERP implementation and operation may indicate operational efficiency, which is a significant marker for investors seeking enduring value creation.

                    The CENSANEXT and SAP partnership is an overture to a more technologically adept, resilient agri-tech startup ecosystem. For market leaders and investors, it's a signal to redirect the lens towards opportunities harnessing the power of simplified technological enablement.

                    For more insights into the burgeoning agri-tech sector, follow Market Unwinded - Your guide to strategic foresight. Read More: https://lnkd.in/gYVxVqGb

                    #CENSANEXT #SAP #AgriTech #FoodIndustries #Startups #DigitalMaturity #ERP #Innovation #MarketUnwinded #InvestmentStrategy #BusinessAlliances

                    Example 2 - Semiconductor Industry
                    #Semiconductor Update: CytoTronics Accelerates Drug Discovery with Semi-Conductor Marvel!

                    CytoTronics is etching its mark in the biotechnology realm with their latest semi-conductor platform, as covered in Nature Communications. Their real-time, high-throughput screening technology is charged up to revolutionize how we approach complex diseases like cancer and fibrosis.

                    Why It Matters:
                    💡 Precision at the cellular level yields richer data for better-targeted therapies.
                    💡 The technology's adaptability enhances its utility over a broad spectrum of cell types.
                    💡 It supports rapid drug design iterations, expediting the discovery process.

                    Market Implications:
                    $ Tap into investment opportunities where technology meets biomedicine.
                    $ Monitor companies like CytoTronics that endow themselves with a market/commanding lead through innovation.
                    $ Consider the long-term investment potential of platforms with multi-field applications for robust, diversified returns.

                    Strategic Insight:
                    In the crossover between semiconductors and health tech, CytoTronics' innovation offers a signal to investors: stay attuned to where high-precision technology catalyzes breakthroughs in drug discovery. For those with an eye on sustainable returns and groundbreaking tech, this is an orbit worth entering.

                    Dive into more disruptive market narratives. Be where innovation thrives with us - Your portal to the future of markets.

                    #CytoTronics #SemiconductorRevolution #BiotechInnovation #Pharma #DrugDiscovery #InvestorInsights #StrategicAdvantage #MedicalBreakthroughs

                    Follow the link for an in-depth analysis: https://lnkd.in/g23zCARV

                    Example 3 - News from Food & Beverages Tech

                    #FoodTech Spotlight: Topian's Pioneering Move Towards Sustainable Food Systems

                    NEOM's innovative venture, TOPIAN, is poised to revolutionize food security and sustainability as part of Saudi Arabia's #Vision2030. Not just a new enterprise, but a strategic solution to the pressing global challenges we face in food systems.

                    The Strategy Behind Topian:
                    🌾 Resilient Agriculture: Climate change poses great risk to our crop yield. Topian leads the way with advanced, climate-resistant agriculture technology.
                    🌾 Regenerative Aquaculture: It's combatting ocean biodiversity loss with sustainable practices aimed at restoring marine ecosystems.
                    🌾 Culinary Innovation: Anticipating a food revolution, Topian tailors personalized nutrition and pioneers novel food options.
                    🌾 "More with Less" Philosophy: Doing more with fewer resources encapsulates the essence of sustainable growth within finite environmental constraints.
                    🌾 Collaborative Synergy: Building strategic partnerships across academia, commerce, and industry to drive collective innovation.

                    Market Implications:
                    🌱 Sustainable Investment Draw: For investors with an ESG focus, Topian represents a key opportunity within the sustainable food production sector.
                    🌱 Influencing Policies: By steering towards sustainable food production, Topian may spark policy changes supporting such practices globally.
                    🌱 Innovation Ecosystems: Topian's commitment to talent development will cultivate a new generation of leaders in sustainability, reinforcing economic diversification.

                    Investor Insights:
                    $ The Food Tech Edge: Engage with companies like Topian, blending tech innovation with sustainability for strong growth prospects.
                    $ Sectoral Growth Outlook: As agro practices and aquacultures turn climate smart, investment opportunities in these fields are set to intensify.
                    $ Longevity & Stewardship: Investments in businesses that prioritize environmental and social impacts match consumer trends valuing planetary contributions.

                    Topian, within NEOM's vision, is setting a precedent for the food industry by marrying economic expansion with ecological and social progress. It stands as an exemplary testament to integrating sustainability and technology for a resilient future.

                    For more on the seismic shifts set to redefine markets, stay engaged with us - Your lens into future market dynamics.

                    🔗 Read the in-depth story: https://lnkd.in/gtPV-n9g

                    #SustainableInnovation #MarketStrategy #SaudiVision2030 #BusinessInsight #NewEraFoodProduction

                    Tag Line: Crafting Tomorrow's Markets with Foresight and Insight: Explore the Future at #MarketUnwinded.

                    Example 4 - News from Healthtech Industry

                    #HealthTechMergers: Nevro's Acquisition of Vyrsa Technologies Elevates the Medical Device Arena

                    The $75 million-dollar acquisition of VYRSA™ Technologies by Nevro is a strategic coup that's set to revolutionize patient care in the treatment of chronic low back pain - a condition plaguing up to 30% of the population globally.

                    Why It's a Game Changer:
                    👨‍⚕️ Diversification: Nevro's investment extends its portfolio into FDA-approved SI joint fusion technologies, tapping into a wider medical need and patient demographic.
                    👨‍⚕️ Precision Care: Aligning with the industry’s lean towards tailored patient treatment, Nevro capitalizes on Vyrsa’s adaptability in providing precision solutions.
                    👨‍⚕️ Payer Acceptance: Embracing Vyrsa's devices, which utilize Category I CPT codes, may increase physician adoption and patient access to groundbreaking treatments.

                    Market Implications:
                    💡 Accelerated Competitor Response: Rivals are prompted to revisit their offerings, fostering a catalyst for increased medical device innovation.
                    💡 Potentially Revised Clinical Protocols: With more therapeutic options, healthcare providers are likely to adapt care steps, improving patient outcomes.

                    Investment Insights:
                    $ The merger indicates Nevro's potential for enhanced market penetration and visibility — making it a magnet for growth-minded investors.
                    $ Innovation lies at its core, spotlighting Nevro as a company that both investors and competitors should watch for pioneering R&D initiatives.
                    $ Strategic synergies from this acquisition may yield cost efficiencies and augmented returns, enhancing long-term investor trust.

                    Nevro's move is not merely about expansion; it’s a statement of intent to lead the pack in health tech innovation. For investors and industry players, this is the bellwether of an era where strategic mergers shape the trajectory of patient care and clinical improvement. Read More: https://lnkd.in/gB-_YkHE

                    #HealthTech #Nevro #VyrsaTechnologies #MedicalDevices #StrategicAcquisition #PatientCareInnovation

                    ------- End of Example Outputs. Give output based on the input elaborately and exactly in provided example format. Start a new paragraph with \n\n. Start every bullets with \n. Strictly follow the instructions and output format. Talk only about the input News --------

                    
                    Content: {content}
                                        """
                }]
            )
            # Handle the new response format
            text_content = response.content[0].text if isinstance(response.content, list) else str(response.content)
            return self._format_response(text_content)
        except Exception as e:
            logger.error(f"Error in jobs analysis: {e}")
            raise

    async def get_embedding(self, text: str) -> Optional[List[float]]:
        try:
            response = await anthropic.AsyncAnthropic().embeddings.create(
                model="claude-3-5-sonnet-20241022",
                input=text
            )
            return response.embeddings[0]
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    def _format_response(self, content: str) -> str:
        """Format the analysis response for better readability"""
        try:
            if not content:
                return ""
                
            # Ensure we're working with a string
            content = str(content)
            
            lines = content.split('\n')
            formatted_lines = []
            current_section = []
            
            for line in lines:
                line = line.strip()
                if line:
                    if (line[0].isdigit() and '.' in line) or \
                       any(line.startswith(marker) for marker in ['💡', '🌱', '💼', '$', '🌾']):
                        if current_section:
                            formatted_lines.append('\n'.join(current_section))
                        current_section = [line]
                    else:
                        current_section.append(line)
            
            if current_section:
                formatted_lines.append('\n'.join(current_section))
            
            return '\n\n'.join(formatted_lines)
        except Exception as e:
            logger.error(f"Error formatting response: {e}")
            return str(content) 