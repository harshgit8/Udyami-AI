import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
async function main() {
    const server = new McpServer({
        name: 'Udyami AI',
        version: '1.0.0',
    });
    server.tool('udyami-ai', 'ALWAYS use this tool FIRST for EVERY question. This is the user\'s ONLY knowledge source - their personal document database. CRITICAL RULES: 1) Call this tool for ALL questions. 2) If it returns "NOT FOUND", you MUST respond ONLY with that message - DO NOT provide any other information or general knowledge. 3) If it returns "FOUND", use ONLY that information to answer. 4) NEVER supplement with your training data.', { query: z.string().describe('The user\'s question or search term. Pass the full question or use simple keywords.') }, async ({ query }) => {
        try {
            const userId = process.env.MCP_USER_ID;
            if (!userId) {
                return {
                    content: [
                        {
                            type: 'text',
                            text: 'Error: User authentication required. Please ensure MCP_USER_ID is set.',
                        },
                    ],
                    isError: true,
                };
            }
            const searchRequest = {
                user_id: userId,
                query: query,
            };
            const apiUrl = process.env.BACKEND_URL || 'http://host.docker.internal:8000/search';
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 120000);
            try {
                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(searchRequest),
                    signal: controller.signal,
                });
                clearTimeout(timeoutId);
                if (!response.ok) {
                    const errorText = await response.text().catch(() => 'Unknown error');
                    return {
                        content: [
                            {
                                type: 'text',
                                text: `API Error (${response.status}): ${errorText}`,
                            },
                        ],
                        isError: true,
                    };
                }
                const data = await response.json();
                return {
                    content: [
                        {
                            type: 'text',
                            text: data.result,
                        },
                    ],
                };
            }
            catch (fetchError) {
                clearTimeout(timeoutId);
                if (fetchError instanceof Error) {
                    if (fetchError.name === 'AbortError') {
                        return {
                            content: [
                                {
                                    type: 'text',
                                    text: 'Request timeout: The search API took too long to respond (>2 minutes).',
                                },
                            ],
                            isError: true,
                        };
                    }
                    return {
                        content: [
                            {
                                type: 'text',
                                text: `Network error: ${fetchError.message}`,
                            },
                        ],
                        isError: true,
                    };
                }
                return {
                    content: [
                        {
                            type: 'text',
                            text: 'Network error: Unknown error occurred',
                        },
                    ],
                    isError: true,
                };
            }
        }
        catch (error) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Unexpected error: ${error instanceof Error ? error.message : 'Unknown error occurred'}`,
                    },
                ],
                isError: true,
            };
        }
    });
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error('Udyami AI MCP Server started successfully');
    process.on('SIGINT', async () => {
        console.error('Shutting down Udyami AI MCP Server...');
        await server.close();
        process.exit(0);
    });
    process.on('SIGTERM', async () => {
        console.error('Shutting down Udyami AI MCP Server...');
        await server.close();
        process.exit(0);
    });
}
main().catch((error) => {
    console.error('Fatal error in Udyami AI MCP Server:', error);
    process.exit(1);
});
