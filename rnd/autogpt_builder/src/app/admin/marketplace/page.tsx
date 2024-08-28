import { withRoleAccess } from "@/lib/withRoleAccess";
import MarketplaceAPI from "@/lib/marketplace-api";
import { Agent } from "@/lib/marketplace-api/";
import React from "react";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";

async function AdminMarketplace() {
  const agents = await getReviewableAgents();
  return (
    <div>
      {agents.agents.map((agent) => (
        <AdminMarketplaceCard agent={agent} key={agent.id} />
      )
      )}
    </div>
  );
}

async function AdminMarketplaceCard({ agent }: { agent: Agent }) {
  const approveAgentWithId = approveAgent.bind(null, agent.id);
  const rejectAgentWithId = rejectAgent.bind(null, agent.id);

  return (
    <Card key={agent.id} className="m-3 p-4 flex flex-col h-[300px]">
      <div className="flex justify-between items-start mb-2">
        <Link href={`/marketplace/${agent.id}`} className="text-lg font-semibold hover:underline">
          {agent.name}
        </Link>
        <Badge variant="outline">v{agent.version}</Badge>
      </div>
      <p className="text-sm text-gray-500 mb-2">by {agent.author}</p>
      <ScrollArea className="flex-grow">
        <p className="text-sm text-gray-600 mb-2">{agent.description}</p>
        <div className="flex flex-wrap gap-1 mb-2">
          {agent.categories.map((category) => (
            <Badge key={category} variant="secondary">{category}</Badge>
          ))}
        </div>
        <div className="flex flex-wrap gap-1">
          {agent.keywords.map((keyword) => (
            <Badge key={keyword} variant="outline">{keyword}</Badge>
          ))}
        </div>
      </ScrollArea>
      <div className="flex justify-between text-xs text-gray-500 mb-2">
        <span>Created: {new Date(agent.createdAt).toLocaleDateString()}</span>
        <span>Updated: {new Date(agent.updatedAt).toLocaleDateString()}</span>
      </div>
      <div className="flex justify-between text-sm mb-4">
        <span>👁 {agent.views}</span>
        <span>⬇️ {agent.downloads}</span>
      </div>
      <div className="flex justify-end space-x-2 mt-auto">
        <form action={rejectAgentWithId}>
          <Button variant="outline" type="submit">
            Reject
          </Button>
        </form>
        <form action={approveAgentWithId}>
          <Button type="submit">
            Approve
          </Button>
        </form>
      </div>
    </Card>
  );
}


async function approveAgent(agentId: string) {
  "use server";
  console.log(`Approving agent ${agentId}`);
}

async function rejectAgent(agentId: string) {
  "use server";
  console.log(`Rejecting agent ${agentId}`);
}

async function getReviewableAgents() {
  'use server';
  const api = new MarketplaceAPI();
  return api.getAgentSubmissions();

}


export default async function AdminDashboardPage() {
  "use server";
  const withAdminAccess = await withRoleAccess(["admin"]);
  const ProtectedAdminMarketplace = await withAdminAccess(AdminMarketplace);
  return <ProtectedAdminMarketplace />;
}
