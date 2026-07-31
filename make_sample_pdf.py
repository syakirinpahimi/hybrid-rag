from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate

BODY = """Nova Dynamics is an enterprise AI analytics company headquartered in Austin, Texas. The company was founded in 2012 by Elena Vasquez, who still serves as chief executive officer. Nova Dynamics employs roughly 2,400 people across offices in Austin, Zurich, and Singapore. Its flagship product, the Aurora analytics platform, is used by more than 300 enterprise customers worldwide. The company reported revenue of 480 million dollars in 2024, up from 310 million dollars in 2023. Analysts attribute the growth to Aurora's expanding customer base and the integration of quantum simulation features.

In early 2024, Nova Dynamics acquired Quantum Leap Labs, a quantum computing startup based in Zurich. Quantum Leap Labs was founded in 2015 by Marcus Webb, a former physicist at CERN. The acquisition closed at a price of 1.2 billion dollars, making it Nova Dynamics' largest deal to date. As part of the acquisition, Marcus Webb joined Nova Dynamics as chief technology officer. Quantum Leap Labs' flagship product, the Qube quantum simulator, was subsequently integrated into the Aurora platform. The Zurich office, previously Quantum Leap Labs' headquarters, became Nova Dynamics' European headquarters and now hosts the company's quantum research division.

Nova Dynamics maintains a close partnership with Helix Robotics, a logistics robotics company founded in 2018 by David Chen in Toronto. The two companies signed a partnership agreement in 2023 to deploy Helix's Helios warehouse robot inside Nova Dynamics' fulfillment centers. By the end of 2025, more than 1,200 Helios units were operating in Nova facilities across North America. In 2025 the partnership was extended with a joint research and development facility in Toronto focused on autonomous retrieval systems for high-value inventory.

On the energy side, Nova Dynamics works with Vertex Energy, a grid-scale battery provider. Vertex Energy was founded in 2016 and is led by chief executive officer Amara Okafor, who joined the company in 2019. In 2025, Vertex Energy raised a 300 million dollar Series D round led by Polaris Capital. Vertex Energy's battery systems now power the primary data centers that run the Aurora platform. Polaris Capital is a venture firm founded in 2009 and is also an investor in Helix Robotics, having led the company's Series B round in 2021.

Nova Dynamics runs Aurora on infrastructure provided by Bluefin Cloud, a Seattle-based cloud provider founded in 2016 by Raj Mehta. The two companies signed a multi-year infrastructure contract in 2022 valued at approximately 90 million dollars per year. Bluefin Cloud hosts Aurora's workloads across three regions and provides Nova Dynamics with guaranteed uptime service level agreements. The contract includes a clause allowing Nova Dynamics to expand capacity without renegotiation through 2027.

Looking ahead, Nova Dynamics plans to launch Aurora 2.0 in the third quarter of 2026. The new release will embed the Qube quantum simulator directly in the platform's optimization engine. The company targets 800 million dollars in revenue for 2026 and is expanding its engineering teams in Austin and Zurich. Helix Robotics expects to ship 5,000 additional Helios units in 2026. Analysts note that a potential Nova Dynamics initial public offering is being discussed for 2027, though the company has not confirmed any timeline."""

POLARIS_BODY = """Polaris Capital is a venture capital firm headquartered in Boston, Massachusetts. The firm was founded in 2009 by managing partner Daniel Roth. Polaris invests across enterprise software, energy infrastructure, and industrial automation. The firm closed its second flagship fund, Polaris II, at 500 million dollars in 2023, and allocates roughly a third of the fund to early stage infrastructure companies.

Partner Sarah Kim joined Polaris in 2013 and leads the firm's enterprise infrastructure practice. Kim represents Polaris on the board of Vertex Energy and holds an observer seat at Helix Robotics. In internal correspondence, Kim has described the portfolio's thesis as backing companies that form the physical backbone of the AI economy: energy storage, robotics, and logistics.

The Polaris portfolio includes three companies of note. Vertex Energy, a grid-scale battery provider led by chief executive officer Amara Okafor, raised a 300 million dollar Series D round in 2025 with Polaris Capital as lead investor. Helix Robotics, a Toronto-based autonomous warehouse robotics company, raised a 45 million dollar Series B round in 2021 with Polaris as the lead investor. Northwind Logistics, a freight and fulfillment operator based in Atlanta, raised a 20 million dollar Series A round in 2022 with Polaris as the lead investor. Northwind began deploying Helix Robotics' Helios units in its regional distribution centers in 2025, an example of the synergies the firm encourages across its portfolio companies.

Polaris typically takes board seats in companies where it leads rounds and observes in earlier-stage positions. The firm is headquartered in Boston but maintains advisory offices in New York and San Francisco. Polaris does not disclose management fees, though partners have noted the firm targets fund sizes that allow concentrated positions in its highest-conviction companies. The firm plans to begin marketing Polaris III in 2027 with a target of 700 million dollars."""

HELIOS_BODY = """Helix Robotics designs and manufactures autonomous mobile robots for warehouse and fulfillment operations. The company was founded in 2018 by David Chen and is headquartered in Toronto, Canada. Helix's chief technology officer is Priya Sharma, who joined the company in 2019 from Boston Dynamics, where she led the perception team for the Stretch robot. Helix operates a 40,000 square foot manufacturing facility in Mississauga, Ontario, and expects to double production capacity by the end of 2026.

The company's flagship product is the Helios autonomous mobile robot. Helios is rated to carry a payload of 25 kilograms and operates for up to 8 hours on a single battery charge. The robot navigates using a combination of LiDAR and a 3D computer vision stack, reaching a top speed of 3 meters per second in corridors. Helios is designed for high-density pallet handling and can swap batteries without halting a fulfillment shift. Each unit is covered by a five-year service contract that includes predictive maintenance through Helix's cloud fleet-management portal.

Helix's largest customer is Nova Dynamics, which began deploying Helios units in 2023 under a partnership agreement and operated more than 1,200 units across its North American fulfillment centers by the end of 2025. Northwind Logistics, a freight and fulfillment operator based in Atlanta, placed a 300-unit order in 2025, with deliveries scheduled through 2026. Helix also runs a joint research and development facility with Nova Dynamics in Toronto focused on autonomous retrieval systems for high-value inventory.

On the roadmap, Helix plans to launch Helios 2 in the fourth quarter of 2026 with a 40 kilogram payload capacity and extended eight-and-a-half-hour runtime. The company expects to ship 5,000 additional Helios units in 2026 across its existing customer base. Helix continues to evaluate entry into grocery e-commerce fulfilment, though management has not committed to a timeline for that market."""

WEBB_BODY = """Marcus Webb is a Swiss physicist and entrepreneur best known for founding Quantum Leap Labs, the quantum computing startup acquired by Nova Dynamics in 2024. Webb grew up in Zurich and studied at ETH Zurich, completing a PhD in quantum computing in 2010. After graduating, he spent four years as a research physicist at CERN, where he worked on error-correction protocols for trapped-ion experiments.

In 2015, Webb founded Quantum Leap Labs in Zurich with a small team of former CERN and ETH colleagues. The company developed the Qube quantum simulator, a desktop-scale device that Nova Dynamics later integrated into its Aurora analytics platform. Nova Dynamics acquired Quantum Leap Labs in 2024 for 1.2 billion dollars, and Webb joined the acquirer as chief technology officer. In that role, Webb leads Nova's quantum research division, which operates out of the former Quantum Leap Labs headquarters in Zurich.

Outside Nova Dynamics, Webb serves as an advisor to Quantum Ventures, a Geneva-based venture fund launched in 2025 that invests in quantum computing and photonics startups. Webb has said he advises no more than three companies at a time, preferring deep engagement with early-stage founders. He also mentors university spinoff teams through an annual residency program hosted at ETH Zurich.

Webb lives in Zurich with his family and is a frequent speaker at European quantum computing conferences. Colleagues describe him as a demanding but generous engineer, known for reading grant applications line by line. In interviews, Webb has emphasized that commercial quantum advantage will come from narrow applications first, which is why he pushed to ship the Qube as a specialized simulator rather than wait for a general-purpose quantum computer."""


DOCS = [
    ("industry_report.pdf", "Nova Dynamics: A Decade of Deals in Enterprise AI", BODY),
    ("polaris_portfolio_memo.pdf", "Polaris Capital: Portfolio Overview (Internal)", POLARIS_BODY),
    ("helios_technical_brief.pdf", "Helix Robotics: Helios Autonomous Mobile Robot - Technical Brief", HELIOS_BODY),
    ("marcus_webb_profile.pdf", "Marcus Webb: From CERN to Quantum Leap Labs", WEBB_BODY),
]


def main() -> None:
    out_dir = Path(__file__).parent / "sample"
    out_dir.mkdir(exist_ok=True)
    styles = getSampleStyleSheet()
    for filename, title, body in DOCS:
        doc = SimpleDocTemplate(str(out_dir / filename), pagesize=letter)
        flowables = [Paragraph(title, styles["Title"])]
        flowables += [Paragraph(p, styles["BodyText"]) for p in body.split("\n\n")]
        doc.build(flowables)
        print(f"wrote {out_dir / filename}")


if __name__ == "__main__":
    main()
