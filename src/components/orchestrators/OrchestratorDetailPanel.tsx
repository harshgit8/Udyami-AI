import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { motion, AnimatePresence } from "framer-motion";
import { ProductionSchedulingDetail } from "./details/ProductionSchedulingDetail";
import { QuotationGeneratorDetail } from "./details/QuotationGeneratorDetail";
import { InvoiceGenerationDetail } from "./details/InvoiceGenerationDetail";
import { QualityIntelligenceDetail } from "./details/QualityIntelligenceDetail";
import { RnDFormulationDetail } from "./details/RnDFormulationDetail";
import { WhatIfSimulatorDetail } from "./details/WhatIfSimulatorDetail";
import { PredictivePricingDetail } from "./details/PredictivePricingDetail";
import { ProductionRecommendationDetail } from "./details/ProductionRecommendationDetail";
import { SupplierAuctionDetail } from "./details/SupplierAuctionDetail";
import { CarbonFootprintDetail } from "./details/CarbonFootprintDetail";
import { VoiceOfCustomerDetail } from "./details/VoiceOfCustomerDetail";
import { NegotiationAgentsDetail } from "./details/NegotiationAgentsDetail";
import { WorkforceWellbeingDetail } from "./details/WorkforceWellbeingDetail";

interface OrchestratorDetailPanelProps {
  orchestratorId: string | null;
  onClose: () => void;
}

const detailComponents: Record<string, React.ComponentType> = {
  "production-scheduling": ProductionSchedulingDetail,
  "quotation-generator": QuotationGeneratorDetail,
  "invoice-generation": InvoiceGenerationDetail,
  "quality-intelligence": QualityIntelligenceDetail,
  "rnd-formulation": RnDFormulationDetail,
  "what-if-simulator": WhatIfSimulatorDetail,
  "predictive-pricing": PredictivePricingDetail,
  "production-recommendation": ProductionRecommendationDetail,
  "supplier-auction": SupplierAuctionDetail,
  "carbon-footprint": CarbonFootprintDetail,
  "voice-of-customer": VoiceOfCustomerDetail,
  "negotiation-agents": NegotiationAgentsDetail,
  "workforce-wellbeing": WorkforceWellbeingDetail,
};

const titles: Record<string, { title: string; description: string }> = {
  "production-scheduling": { title: "Production Scheduling AI", description: "Optimizes production schedules based on machine capacity and orders" },
  "quotation-generator": { title: "Quotation Generator AI", description: "Creates intelligent quotations based on costs, demand, and market analysis" },
  "invoice-generation": { title: "Invoice Generation AI", description: "Creates GST-compliant invoices with automatic calculations" },
  "quality-intelligence": { title: "Quality Intelligence AI", description: "Detects defects and analyzes production quality using sensor data" },
  "rnd-formulation": { title: "R&D Formulation AI", description: "Suggests new product formulations using genetic algorithms" },
  "what-if-simulator": { title: "What-If Scenario Simulator", description: "Simulate machine failure, material shortage, rush orders and price changes" },
  "predictive-pricing": { title: "Predictive Pricing Engine", description: "AI recommends optimal selling price based on cost and market demand" },
  "production-recommendation": { title: "Production Recommendation", description: "Netflix-style next product recommendation based on historical data" },
  "supplier-auction": { title: "Supplier Reverse Auction", description: "Suppliers compete in real-time to offer the lowest price" },
  "carbon-footprint": { title: "Carbon Footprint Tracker", description: "Tracks CO₂ emissions per product with sustainability scoring" },
  "voice-of-customer": { title: "Voice of Customer AI", description: "Analyzes customer reviews and complaints for sentiment insights" },
  "negotiation-agents": { title: "Auto-Negotiation Agents", description: "AI negotiates with suppliers automatically for best deals" },
  "workforce-wellbeing": { title: "Workforce Wellbeing AI", description: "Detects worker fatigue, safety risks, and optimizes shifts" },
};

export function OrchestratorDetailPanel({ orchestratorId, onClose }: OrchestratorDetailPanelProps) {
  const DetailComponent = orchestratorId ? detailComponents[orchestratorId] : null;
  const info = orchestratorId ? titles[orchestratorId] : null;

  return (
    <Dialog open={!!orchestratorId} onOpenChange={() => onClose()}>
      <DialogContent className="max-w-4xl max-h-[85vh] overflow-y-auto p-0">
        {info && (
          <DialogHeader className="p-6 pb-0">
            <DialogTitle className="text-lg">{info.title}</DialogTitle>
            <DialogDescription>{info.description}</DialogDescription>
          </DialogHeader>
        )}
        <div className="p-6 pt-4">
          {DetailComponent && <DetailComponent />}
        </div>
      </DialogContent>
    </Dialog>
  );
}
