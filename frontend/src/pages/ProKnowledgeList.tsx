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
\tconst api = useMemo(() => new ApiService(API_BASE_URL), []);
\tconst [facts, setFacts] = useState<FactItem[]>([]);
\tconst [page, setPage] = useState<number>(1);
\tconst [perPage, setPerPage] = useState<number>(50);
\tconst [total, setTotal] = useState<number>(0);
\tconst [loading, setLoading] = useState<boolean>(false);
\tconst [error, setError] = useState<string | null>(null);
\tconst [search, setSearch] = useState<string>('');

\tconst loadPage = useCallback(async (nextPage: number, nextPerPage: number) => {
\t\tsetLoading(true);
\t\tsetError(null);
\t\ttry {
\t\t\t// Server-seitige Pagination
\t\t\tconst data = await api.getFactsPaginated(nextPage, nextPerPage);
\t\t\tsetFacts(data.facts || []);
\t\t\tsetTotal(data.total || 0);
\t\t} catch (e: any) {
\t\t\tsetError(e?.message || 'Laden fehlgeschlagen');
\t\t} finally {
\t\t\tsetLoading(false);
\t\t}
\t}, [api]);

\tuseEffect(() => {
\t\tloadPage(page, perPage);
\t}, [page, perPage, loadPage]);

\tconst totalPages = Math.max(1, Math.ceil(total / perPage));

\tconst Row = ({ index, style }: { index: number; style: React.CSSProperties }) => {
\t\tconst fact = facts[index];
\t\tif (!fact) return null;
\t\treturn (
\t\t\t<div style={style} className="px-3 py-2">
\t\t\t\t<Card className="p-3">
\t\t\t\t\t<div className="flex items-start justify-between gap-2">
\t\t\t\t\t\t<code className="text-sm font-mono break-all">{fact.statement}</code>
\t\t\t\t\t\t<div className="flex items-center gap-2 ml-2 shrink-0">
\t\t\t\t\t\t\t{typeof fact.id !== 'undefined' && (
\t\t\t\t\t\t\t\t<Badge variant="outline">#{fact.id}</Badge>
\t\t\t\t\t\t\t)}
\t\t\t\t\t\t\t{typeof fact.confidence === 'number' && (
\t\t\t\t\t\t\t\t<Badge variant={fact.confidence > 0.8 ? 'default' : 'secondary'}>
\t\t\t\t\t\t\t\t\t{Math.round(fact.confidence * 100)}%
\t\t\t\t\t\t\t\t</Badge>
\t\t\t\t\t\t\t)}
\t\t\t\t\t\t</div>
\t\t\t\t\t</div>
\t\t\t\t</Card>
\t\t\t</div>
\t\t);
\t};

\tconst handleFirst = () => setPage(1);
\tconst handlePrev = () => setPage(p => Math.max(1, p - 1));
\tconst handleNext = () => setPage(p => Math.min(totalPages, p + 1));
\tconst handleLast = () => setPage(totalPages);

\tconst [stats, setStats] = useState<any>(null);
\tconst refreshStats = useCallback(async () => {
\t\ttry {
\t\t\tconst s = await api.getFactsStats(5000);
\t\t\tsetStats(s);
\t\t} catch {}
\t}, [api]);

\tuseEffect(() => { refreshStats(); }, [refreshStats]);

\tconst [bulkText, setBulkText] = useState<string>('');
\tconst [bulkBusy, setBulkBusy] = useState<boolean>(false);
\tconst doBulkImport = async () => {
\t\tconst statements = bulkText
\t\t\t.split(/\r?\n/)
\t\t\t.map(s => s.trim())
\t\t\t.filter(s => s.length > 0);
\t\tif (statements.length === 0) return;
\t\tsetBulkBusy(true);
\t\ttry {
\t\t\tawait api.bulkInsert(statements);
\t\t\tsetBulkText('');
\t\t\tawait loadPage(page, perPage);
\t\t\tawait refreshStats();
\t\t} finally {
\t\t\tsetBulkBusy(false);
\t\t}
\t};

\treturn (
\t\t<div className="h-full flex flex-col p-4 gap-4">
\t\t\t{/* Header Controls */}
\t\t\t<div className="flex flex-wrap items-center gap-3">
\t\t\t\t<div className="text-sm text-muted-foreground">
\t\t\t\t\t{total.toLocaleString()} Facts • Page {page} / {totalPages}
\t\t\t\t</div>
\t\t\t\t<div className="flex items-center gap-2 ml-auto">
\t\t\t\t\t<Button variant="outline" onClick={handleFirst} disabled={page === 1}>First</Button>
\t\t\t\t\t<Button variant="outline" onClick={handlePrev} disabled={page === 1}>Previous</Button>
\t\t\t\t\t<Input
\t\t\t\t\t\ttype="number"
\t\t\t\t\t\tvalue={page}
\t\t\t\t\t\tmin={1}
\t\t\t\t\t\tmax={totalPages}
\t\t\t\t\t\tonChange={(e) => setPage(Math.max(1, Math.min(totalPages, Number(e.target.value) || 1)))}
\t\t\t\t\t\tclassName="w-20"
\t\t\t\t\t/>
\t\t\t\t\t<Button variant="outline" onClick={handleNext} disabled={page === totalPages}>Next</Button>
\t\t\t\t\t<Button variant="outline" onClick={handleLast} disabled={page === totalPages}>Last</Button>
\t\t\t\t\t<select
\t\t\t\t\t\tclassName="border rounded px-2 py-1 text-sm"
\t\t\t\t\t\tvalue={perPage}
\t\t\t\t\t\tonChange={(e) => { setPerPage(Number(e.target.value)); setPage(1); }}
\t\t\t\t\t>
\t\t\t\t\t\t{PER_PAGE_OPTIONS.map(v => (
\t\t\t\t\t\t\t<option key={v} value={v}>{v}/page</option>
\t\t\t\t\t\t))}
\t\t\t\t\t</select>
\t\t\t\t</div>
\t\t\t</div>

\t\t\t{/* Search (client-seitig – optional) */}
\t\t\t<div className="flex items-center gap-2">
\t\t\t\t<Input
\t\t\t\t\tplaceholder="Suche (Client-Filter auf aktuelle Seite)"
\t\t\t\t\tvalue={search}
\t\t\t\t\tonChange={(e) => setSearch(e.target.value)}
\t\t\t\t\tclassName="max-w-sm"
\t\t\t\t/>
\t\t\t\t<Button variant="outline" onClick={() => { setSearch(''); }}>Reset</Button>
\t\t\t</div>

\t\t\t{/* List */}
\t\t\t<div className="flex-1 min-h-0">
\t\t\t\t{error && (
\t\t\t\t\t<div className="text-sm text-red-500 mb-2">{error}</div>
\t\t\t\t)}
\t\t\t\t<Card className="h-full">
\t\t\t\t\t<ScrollArea className="h-full">
\t\t\t\t\t\t<FixedSizeList
\t\t\t\t\t\t\theight={600}
\t\t\t\t\t\t\titemCount={facts.filter(f => !search || f.statement.toLowerCase().includes(search.toLowerCase())).length}
\t\t\t\t\t\t\titemSize={ROW_HEIGHT}
\t\t\t\t\t\t\twidth="100%"
\t\t\t\t\t\t\toverScanCount={5 as any}
\t\t\t\t\t\t>
\t\t\t\t\t\t\t{({ index, style }) => {
\t\t\t\t\t\t\t\tconst data = facts.filter(f => !search || f.statement.toLowerCase().includes(search.toLowerCase()));
\t\t\t\t\t\t\t\tconst item = data[index];
\t\t\t\t\t\t\t\tif (!item) return null;
\t\t\t\t\t\t\t\treturn (
\t\t\t\t\t\t\t\t\t<div style={style} className="px-3 py-2">
\t\t\t\t\t\t\t\t\t\t<Card className="p-3">
\t\t\t\t\t\t\t\t\t\t\t<div className="flex items-start justify-between gap-2">
\t\t\t\t\t\t\t\t\t\t\t\t<code className="text-sm font-mono break-all">{item.statement}</code>
\t\t\t\t\t\t\t\t\t\t\t\t<div className="flex items-center gap-2 ml-2 shrink-0">
\t\t\t\t\t\t\t\t\t\t\t\t\t{typeof item.id !== 'undefined' && (
\t\t\t\t\t\t\t\t\t\t\t\t\t\t<Badge variant="outline">#{item.id}</Badge>
\t\t\t\t\t\t\t\t\t\t\t\t\t)}
\t\t\t\t\t\t\t\t\t\t\t\t\t{typeof item.confidence === 'number' && (
\t\t\t\t\t\t\t\t\t\t\t\t\t\t<Badge variant={item.confidence > 0.8 ? 'default' : 'secondary'}>
\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t{Math.round(item.confidence * 100)}%
\t\t\t\t\t\t\t\t\t\t\t\t\t\t</Badge>
\t\t\t\t\t\t\t\t\t\t\t\t\t)}
\t\t\t\t\t\t\t\t\t\t\t</div>
\t\t\t\t\t\t\t\t\t\t\t</div>
\t\t\t\t\t\t\t\t\t\t</Card>
\t\t\t\t\t\t\t\t\t</div>
\t\t\t\t\t\t\t\t);
\t\t\t\t\t\t\t}}
\t\t\t\t\t\t/>
\t\t\t\t\t</ScrollArea>
\t\t\t\t</Card>
\t\t\t</div>

\t\t\t{/* Stats + Bulk Import */}
\t\t\t<div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
\t\t\t\t<Card className="p-4">
\t\t\t\t\t<div className="flex items-center justify-between mb-2">
\t\t\t\t\t\t<h3 className="text-sm font-semibold">Stats</h3>
\t\t\t\t\t\t<Button size="sm" variant="outline" onClick={refreshStats}>Refresh</Button>
\t\t\t\t\t</div>
\t\t\t\t\t<div className="text-sm text-muted-foreground mb-2">
\t\t\t\t\t\tTotal: {(stats?.total || total || 0).toLocaleString()}
\t\t\t\t\t</div>
\t\t\t\t\t<div className="flex flex-wrap gap-2">
\t\t\t\t\t\t{Array.isArray(stats?.top_predicates) && stats.top_predicates.slice(0, 10).map((p: any, i: number) => (
\t\t\t\t\t\t\t<Badge key={i} variant="secondary" className="text-xs">{p.predicate || p.name}: {p.count}</Badge>
\t\t\t\t\t\t))}
\t\t\t\t\t</div>
\t\t\t\t</Card>

\t\t\t\t<Card className="p-4">
\t\t\t\t\t<div className="flex items-center justify-between mb-2">
\t\t\t\t\t\t<h3 className="text-sm font-semibold">Bulk Import</h3>
\t\t\t\t\t\t<Button size="sm" onClick={doBulkImport} disabled={bulkBusy || bulkText.trim().length === 0}>
\t\t\t\t\t\t\tImportieren
\t\t\t\t\t\t</Button>
\t\t\t\t\t</div>
\t\t\t\t\t<Textarea
\t\t\t\t\t\tplaceholder="Eine Aussage pro Zeile: Predicate(Entity1, Entity2)."
\t\t\t\t\t\trows={6}
\t\t\t\t\t\tvalue={bulkText}
\t\t\t\t\t\tonChange={(e) => setBulkText(e.target.value)}
\t\t\t\t\t/>
\t\t\t\t\t<div className="text-xs text-muted-foreground mt-1">{bulkText.split(/\r?\n/).filter(s => s.trim().length > 0).length} Statements vorbereitet</div>
\t\t\t\t</Card>
\t\t\t</div>
\t\t</div>
\t);
};

export default ProKnowledgeList;


