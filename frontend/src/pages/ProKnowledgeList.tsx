import React, { useEffect, useMemo, useState, useCallback } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { FixedSizeList } from 'react-window';
import ApiService from '@/services/apiService';
import { API_BASE_URL } from '@/config/backends';

type FactItem = { id?: number; statement: string; confidence?: number; source?: string };

const ROW_HEIGHT = 64;
const PER_PAGE_OPTIONS = [10, 25, 50, 100];

const ProKnowledgeList: React.FC = () => {
	const api = useMemo(() => new ApiService(API_BASE_URL), []);
	const [facts, setFacts] = useState<FactItem[]>([]);
	const [page, setPage] = useState<number>(1);
	const [perPage, setPerPage] = useState<number>(50);
	const [total, setTotal] = useState<number>(0);
	const [loading, setLoading] = useState<boolean>(false);
	const [error, setError] = useState<string | null>(null);
	const [search, setSearch] = useState<string>('');

	const loadPage = useCallback(async (nextPage: number, nextPerPage: number) => {
		setLoading(true);
		setError(null);
		try {
			// Server-seitige Pagination
			const data = await api.getFactsPaginated(nextPage, nextPerPage);
			setFacts(data.facts || []);
			setTotal(data.total || 0);
		} catch (e: any) {
			setError(e?.message || 'Laden fehlgeschlagen');
		} finally {
			setLoading(false);
		}
	}, [api]);

	useEffect(() => {
		loadPage(page, perPage);
	}, [page, perPage, loadPage]);

	const totalPages = Math.max(1, Math.ceil(total / perPage));

	const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => {
		const fact = facts[index];
		if (!fact) return null;
		return (
			<div style={style} className="px-3 py-2">
				<Card className="p-3">
					<div className="flex items-start justify-between gap-2">
						<code className="text-sm font-mono break-all">{fact.statement}</code>
						<div className="flex items-center gap-2 ml-2 shrink-0">
							{typeof fact.id !== 'undefined' && (
								<Badge variant="outline">#{fact.id}</Badge>
							)}
							{typeof fact.confidence === 'number' && (
								<Badge variant={fact.confidence > 0.8 ? 'default' : 'secondary'}>
									{Math.round(fact.confidence * 100)}%
								</Badge>
							)}
						</div>
					</div>
				</Card>
			</div>
		);
	};

	const handleFirst = () => setPage(1);
	const handlePrev = () => setPage(p => Math.max(1, p - 1));
	const handleNext = () => setPage(p => Math.min(totalPages, p + 1));
	const handleLast = () => setPage(totalPages);

	const [stats, setStats] = useState<any>(null);
	const refreshStats = useCallback(async () => {
		try {
			const s = await api.getFactsStats(5000);
			setStats(s);
		} catch {}
	}, [api]);

	useEffect(() => { refreshStats(); }, [refreshStats]);

	const [bulkText, setBulkText] = useState<string>('');
	const [bulkBusy, setBulkBusy] = useState<boolean>(false);
	const [bulkErrors, setBulkErrors] = useState<string | null>(null);
	const [bulkProgress, setBulkProgress] = useState<string | null>(null);
	const doBulkImport = async () => {
		const statements = bulkText
			.split(/\r?\n/)
			.map(s => s.trim())
			.filter(s => s.length > 0);
		if (statements.length === 0) return;
		setBulkBusy(true);
		setBulkErrors(null);
		setBulkProgress(`Importing ${statements.length} facts...`);
		try {
			const res = await api.bulkInsert(statements);
			if (res?.errors && res.errors.length > 0) {
				setBulkErrors(`${res.errors.length} Fehler beim Import. ${res.inserted} von ${res.statements} erfolgreich.`);
			} else {
				setBulkProgress(`✅ ${res.inserted} Facts erfolgreich importiert!`);
			}
			setBulkText('');
			await loadPage(page, perPage);
			await refreshStats();
		} finally {
			setBulkBusy(false);
			setTimeout(() => setBulkProgress(null), 3000);
		}
	};

	// Drag & Drop JSONL Import
	const handleFileImport = async (file: File) => {
		if (!file) return;
		setBulkBusy(true);
		setBulkErrors(null);
		setBulkProgress(`Processing file: ${file.name}...`);
		try {
			const text = await file.text();
			let statements: string[] = [];
			const lines = text.split(/\r?\n/).map(l => l.trim()).filter(Boolean);
			for (const line of lines) {
				try {
					if (line.startsWith('{') && line.endsWith('}')) {
						const obj = JSON.parse(line);
						const st = (obj as any).statement || (obj as any).fact || (obj as any)?.data?.statement;
						if (typeof st === 'string' && st.trim().length > 0) statements.push(st.trim());
					} else {
						statements.push(line);
					}
				} catch {}
			}
			statements = statements.filter(s => s.length > 0);
			if (statements.length === 0) {
				setBulkErrors('Keine importierbaren Statements gefunden.');
				setBulkProgress(null);
				return;
			}
			setBulkProgress(`Importing ${statements.length} facts from file...`);
			const res = await api.bulkInsert(statements);
			if (res?.errors && res.errors.length > 0) {
				setBulkErrors(`${res.errors.length} Fehler beim Import (Datei). ${res.inserted} von ${res.statements} erfolgreich.`);
			} else {
				setBulkProgress(`✅ ${res.inserted} Facts aus Datei importiert!`);
			}
			await loadPage(1, perPage);
			setPage(1);
			await refreshStats();
		} finally {
			setBulkBusy(false);
			setTimeout(() => setBulkProgress(null), 3000);
		}
	};

	// Export-Download
	const [exportLimit, setExportLimit] = useState<number>(100);
	const [exportFormat, setExportFormat] = useState<'json' | 'jsonl'>('jsonl');
	const [exportBusy, setExportBusy] = useState<boolean>(false);
	const doExport = async () => {
		setExportBusy(true);
		try {
			const data = await api.exportFacts(exportLimit, exportFormat);
			let blob: Blob;
			if (exportFormat === 'json') {
				blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
			} else {
				blob = new Blob([data as string], { type: 'application/x-ndjson' });
			}
			const url = URL.createObjectURL(blob);
			const a = document.createElement('a');
			a.href = url;
			a.download = `facts_export_${exportLimit || 'all'}.${exportFormat}`;
			document.body.appendChild(a);
			a.click();
			document.body.removeChild(a);
			URL.revokeObjectURL(url);
		} finally {
			setExportBusy(false);
		}
	};

	return (
		<div className="h-full flex flex-col p-4 gap-4">
			{/* Header Controls */}
			<div className="flex flex-wrap items-center gap-3">
				<div className="text-sm text-muted-foreground">
					{total.toLocaleString()} Facts • Page {page} / {totalPages}
				</div>
				<div className="flex items-center gap-2 ml-auto">
					<Button variant="outline" onClick={handleFirst} disabled={page === 1}>First</Button>
					<Button variant="outline" onClick={handlePrev} disabled={page === 1}>Previous</Button>
					<Input
						type="number"
						value={page}
						min={1}
						max={totalPages}
						onChange={(e) => setPage(Math.max(1, Math.min(totalPages, Number(e.target.value) || 1)))}
						className="w-20"
					/>
					<Button variant="outline" onClick={handleNext} disabled={page === totalPages}>Next</Button>
					<Button variant="outline" onClick={handleLast} disabled={page === totalPages}>Last</Button>
					<select
						className="border rounded px-2 py-1 text-sm"
						value={perPage}
						onChange={(e) => { setPerPage(Number(e.target.value)); setPage(1); }}
					>
						{PER_PAGE_OPTIONS.map(v => (
							<option key={v} value={v}>{v}/page</option>
						))}
					</select>
				</div>
			</div>

			{/* Search (client-seitig – optional) */}
			<div className="flex items-center gap-2">
				<Input
					placeholder="Suche (Client-Filter auf aktuelle Seite)"
					value={search}
					onChange={(e) => setSearch(e.target.value)}
					className="max-w-sm"
				/>
				<Button variant="outline" onClick={() => { setSearch(''); }}>Reset</Button>
			</div>

			{/* List */}
			<div className="flex-1 min-h-0">
				{error && (
					<div className="text-sm text-red-500 mb-2">{error}</div>
				)}
				<Card className="h-full">
					<ScrollArea className="h-full">
						<FixedSizeList
							height={600}
							itemCount={facts.filter(f => !search || f.statement.toLowerCase().includes(search.toLowerCase())).length}
							itemSize={ROW_HEIGHT}
							width="100%"
							overscanCount={5 as any}
						>
							{({ index, style }) => {
								const data = facts.filter(f => !search || f.statement.toLowerCase().includes(search.toLowerCase()));
								const item = data[index];
								if (!item) return null;
								return (
									<div style={style} className="px-3 py-2">
										<Card className="p-3">
											<div className="flex items-start justify-between gap-2">
												<code className="text-sm font-mono break-all">{item.statement}</code>
												<div className="flex items-center gap-2 ml-2 shrink-0">
													{typeof item.id !== 'undefined' && (
														<Badge variant="outline">#{item.id}</Badge>
													)}
													{typeof item.confidence === 'number' && (
														<Badge variant={item.confidence > 0.8 ? 'default' : 'secondary'}>
															{Math.round(item.confidence * 100)}%
														</Badge>
													)}
												</div>
											</div>
										</Card>
									</div>
								);
							}}
						</FixedSizeList>
					</ScrollArea>
				</Card>
			</div>

			{/* Stats + Export + Bulk Import */}
			<div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
				<Card className="p-4">
					<div className="flex items-center justify-between mb-2">
						<h3 className="text-sm font-semibold">Stats</h3>
						<Button size="sm" variant="outline" onClick={refreshStats}>Refresh</Button>
					</div>
					<div className="text-sm text-muted-foreground mb-2">
						Total: {(stats?.total || total || 0).toLocaleString()}
					</div>
					<div className="flex flex-wrap gap-2 mb-2">
						{Array.isArray(stats?.top_predicates) && stats.top_predicates.slice(0, 10).map((p: any, i: number) => (
							<Badge key={i} variant="secondary" className="text-xs">{p.predicate || p.name}: {p.count}</Badge>
						))}
					</div>
					{stats?.activity && (
						<div className="text-xs text-muted-foreground space-y-1">
							<div className="flex items-center justify-between">
								<span>24h</span>
								<div className="flex-1 mx-2 h-2 bg-muted rounded">
									<div className="h-2 bg-primary rounded" style={{ width: `${Math.min(100, (stats.activity.last_24h || 0) / Math.max(1, stats.activity.last_30d || 1) * 100)}%` }} />
								</div>
								<span>{stats.activity.last_24h}</span>
							</div>
							<div className="flex items-center justify-between">
								<span>7d</span>
								<div className="flex-1 mx-2 h-2 bg-muted rounded">
									<div className="h-2 bg-secondary rounded" style={{ width: `${Math.min(100, (stats.activity.last_7d || 0) / Math.max(1, stats.activity.last_30d || 1) * 100)}%` }} />
								</div>
								<span>{stats.activity.last_7d}</span>
							</div>
							<div className="flex items-center justify-between">
								<span>30d</span>
								<div className="flex-1 mx-2 h-2 bg-muted rounded">
									<div className="h-2 bg-foreground/30 rounded" style={{ width: `100%` }} />
								</div>
								<span>{stats.activity.last_30d}</span>
							</div>
						</div>
					)}
				</Card>

				{/* Export Panel */}
				<Card className="p-4">
					<div className="flex items-center justify-between mb-2">
						<h3 className="text-sm font-semibold">Export</h3>
						<Button size="sm" onClick={doExport} disabled={exportBusy}>
							{exportBusy ? 'Export...' : 'Download'}
						</Button>
					</div>
					<div className="flex items-center gap-2">
						<label className="text-xs text-muted-foreground">Limit</label>
						<Input type="number" className="w-24" value={exportLimit} min={0} onChange={(e) => setExportLimit(Math.max(0, Number(e.target.value) || 0))} />
						<select className="border rounded px-2 py-1 text-sm" value={exportFormat} onChange={(e) => setExportFormat((e.target.value as any) || 'jsonl')}>
							<option value="jsonl">JSONL</option>
							<option value="json">JSON</option>
						</select>
					</div>
					<div className="text-xs text-muted-foreground mt-2">Limit 0 = alle Facts</div>
				</Card>

				{/* Bulk Import */}
				<Card className="p-4">
					<div className="flex items-center justify-between mb-2">
						<h3 className="text-sm font-semibold">Bulk Import</h3>
						<Button size="sm" onClick={doBulkImport} disabled={bulkBusy || bulkText.trim().length === 0}>
							Importieren
						</Button>
					</div>
					<Textarea
						placeholder="Eine Aussage pro Zeile: Predicate(Entity1, Entity2)."
						rows={6}
						value={bulkText}
						onChange={(e) => setBulkText(e.target.value)}
					/>
					<div className="text-xs text-muted-foreground mt-1">{bulkText.split(/\r?\n/).filter(s => s.trim().length > 0).length} Statements vorbereitet</div>
					<div className="mt-3 p-3 border border-dashed rounded text-xs text-muted-foreground text-center"
						onDragOver={(e) => { e.preventDefault(); }}
						onDrop={(e) => { e.preventDefault(); const f = (e as any).dataTransfer?.files?.[0]; if (f) handleFileImport(f); }}
					>
						Drag & Drop JSONL-Datei hierher oder
						<label className="ml-1 underline cursor-pointer">
							Datei auswählen
							<input type="file" accept=".jsonl,.json,.txt" className="hidden" onChange={(e) => { const f = (e.target as HTMLInputElement).files?.[0]; if (f) handleFileImport(f); }} />
						</label>
					</div>
					{!bulkBusy && (
						<div className="text-xs text-amber-600 mt-2">
							⚠️ Hinweis: Bulk Import läuft im Kompatibilitätsmodus (einzelne Requests)
						</div>
					)}
					{bulkBusy && <div className="text-xs text-muted-foreground mt-2">Import läuft...</div>}
					{bulkProgress && <div className="text-xs text-primary mt-2">{bulkProgress}</div>}
					{bulkErrors && <div className="text-xs text-red-500 mt-2">{bulkErrors}</div>}
				</Card>
			</div>
		</div>
	);
};

export default ProKnowledgeList;


