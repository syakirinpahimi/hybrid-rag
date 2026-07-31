from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate

TITLE = "Nova Dynamics: A Decade of Deals in Enterprise AI"

BODY = """Nova Dynamics is an enterprise AI analytics company headquartered in Austin, Texas. The company was founded in 2012 by Elena Vasquez, who still serves as chief executive officer. Nova Dynamics employs roughly 2,400 people across offices in Austin, Zurich, and Singapore. Its flagship product, the Aurora analytics platform, is used by more than 300 enterprise customers worldwide. The company reported revenue of 480 million dollars in 2024, up from 310 million dollars in 2023. Analysts attribute the growth to Aurora's expanding customer base and the integration of quantum simulation features.

In early 2024, Nova Dynamics acquired Quantum Leap Labs, a quantum computing startup based in Zurich. Quantum Leap Labs was founded in 2015 by Marcus Webb, a former physicist at CERN. The acquisition closed at a price of 1.2 billion dollars, making it Nova Dynamics' largest deal to date. As part of the acquisition, Marcus Webb joined Nova Dynamics as chief technology officer. Quantum Leap Labs' flagship product, the Qube quantum simulator, was subsequently integrated into the Aurora platform. The Zurich office, previously Quantum Leap Labs' headquarters, became Nova Dynamics' European headquarters and now hosts the company's quantum research division.

Nova Dynamics maintains a close partnership with Helix Robotics, a logistics robotics company founded in 2018 by David Chen in Toronto. The two companies signed a partnership agreement in 2023 to deploy Helix's Helios warehouse robot inside Nova Dynamics' fulfillment centers. By the end of 2025, more than 1,200 Helios units were operating in Nova facilities across North America. In 2025 the partnership was extended with a joint research and development facility in Toronto focused on autonomous retrieval systems for high-value inventory.

On the energy side, Nova Dynamics works with Vertex Energy, a grid-scale battery provider. Vertex Energy was founded in 2016 and is led by chief executive officer Amara Okafor, who joined the company in 2019. In 2025, Vertex Energy raised a 300 million dollar Series D round led by Polaris Capital. Vertex Energy's battery systems now power the primary data centers that run the Aurora platform. Polaris Capital is a venture firm founded in 2009 and is also an investor in Helix Robotics, having led the company's Series B round in 2021.

Nova Dynamics runs Aurora on infrastructure provided by Bluefin Cloud, a Seattle-based cloud provider founded in 2016 by Raj Mehta. The two companies signed a multi-year infrastructure contract in 2022 valued at approximately 90 million dollars per year. Bluefin Cloud hosts Aurora's workloads across three regions and provides Nova Dynamics with guaranteed uptime service level agreements. The contract includes a clause allowing Nova Dynamics to expand capacity without renegotiation through 2027.

Looking ahead, Nova Dynamics plans to launch Aurora 2.0 in the third quarter of 2026. The new release will embed the Qube quantum simulator directly in the platform's optimization engine. The company targets 800 million dollars in revenue for 2026 and is expanding its engineering teams in Austin and Zurich. Helix Robotics expects to ship 5,000 additional Helios units in 2026. Analysts note that a potential Nova Dynamics initial public offering is being discussed for 2027, though the company has not confirmed any timeline."""


def main() -> None:
    out_dir = Path(__file__).parent / "sample"
    out_dir.mkdir(exist_ok=True)
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(out_dir / "industry_report.pdf"), pagesize=letter)
    flowables = [Paragraph(TITLE, styles["Title"])]
    flowables += [Paragraph(p, styles["BodyText"]) for p in BODY.split("\n\n")]
    doc.build(flowables)
    print(f"wrote {out_dir / 'industry_report.pdf'}")


if __name__ == "__main__":
    main()
