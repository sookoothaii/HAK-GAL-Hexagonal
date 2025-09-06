// Minimaler, stiller STDIO-Wrapper für HanzoAI MCP (keine Logs auf stdout/stderr)
// Start: node scripts/hanzoai_mcp_shim.js

(async () => {
	try {
		const baseDir = 'D:/MCP Mods/hanzoai/mcp/dist';
		const sdkBase = 'D:/MCP Mods/hanzoai/mcp/node_modules/@modelcontextprotocol/sdk';
		const toFileUrl = (p) => 'file:///' + p.replace(/\\/g, '/').replace(/ /g, '%20');

		const { Server } = await import(toFileUrl(sdkBase + '/server/index.js'));
		const { StdioServerTransport } = await import(toFileUrl(sdkBase + '/server/stdio.js'));
		const { ListToolsRequestSchema, CallToolRequestSchema, ListResourcesRequestSchema, ReadResourceRequestSchema } = await import(toFileUrl(sdkBase + '/types.js'));

		const toolsMod = await import(toFileUrl(baseDir + '/tools/index.js'));
		const promptsMod = await import(toFileUrl(baseDir + '/prompts/system.js'));
		const allTools = toolsMod.allTools;
		const toolMap = toolsMod.toolMap;
		const getSystemPrompt = promptsMod.getSystemPrompt;

		const server = new Server(
			{ name: 'hanzo-mcp', version: '1.0.0' },
			{ capabilities: { tools: {}, resources: {} } }
		);

		server.setRequestHandler(ListToolsRequestSchema, async () => ({
			tools: allTools.map((t) => ({ name: t.name, description: t.description, inputSchema: t.inputSchema }))
		}));

		server.setRequestHandler(CallToolRequestSchema, async (request) => {
			const tool = toolMap.get(request.params.name);
			if (!tool) {
				return { content: [{ type: 'text', text: `Unknown tool: ${request.params.name}` }], isError: true };
			}
			try {
				return await tool.handler(request.params.arguments || {});
			} catch (e) {
				return { content: [{ type: 'text', text: `Error executing ${tool.name}: ${e?.message || e}` }], isError: true };
			}
		});

		server.setRequestHandler(ListResourcesRequestSchema, async () => ({
			resources: [{ uri: 'hanzo://system-prompt', name: 'System Prompt', mimeType: 'text/plain', description: 'Hanzo MCP system prompt and context' }]
		}));

		server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
			if (request.params.uri === 'hanzo://system-prompt') {
				const systemPrompt = await getSystemPrompt(process.cwd());
				return { contents: [{ uri: request.params.uri, mimeType: 'text/plain', text: systemPrompt }] };
			}
			return { contents: [{ uri: request.params.uri, mimeType: 'text/plain', text: 'Resource not found' }] };
		});

		const transport = new StdioServerTransport();
		await server.connect(transport);
	} catch (_) {
		// keine Ausgabe im STDIO-Modus
	}
})();
