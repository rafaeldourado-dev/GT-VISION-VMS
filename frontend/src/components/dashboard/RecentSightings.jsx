import { useState, useEffect } from 'react';
import apiClient from '@/api/apiClient';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';

export default function RecentSightings() {
    const [sightings, setSightings] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchSightings = async () => {
            try {
                setLoading(true);
                const response = await apiClient.get('/sightings?limit=5');
                setSightings(response.data);
            } catch (error) {
                console.error("Erro ao buscar avistamentos recentes:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchSightings();
    }, []);

    const formatTimestamp = (timestamp) => {
        if (!timestamp) return 'N/A';
        return new Intl.DateTimeFormat('pt-BR', {
            dateStyle: 'short',
            timeStyle: 'medium',
        }).format(new Date(timestamp));
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle>Últimos Avistamentos</CardTitle>
                <CardDescription>As 5 placas mais recentes detectadas pelo sistema.</CardDescription>
            </CardHeader>
            <CardContent>
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Placa</TableHead>
                            <TableHead>Câmera</TableHead>
                            <TableHead className="text-right">Horário</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {loading ? (
                            <TableRow>
                                <TableCell colSpan="3" className="text-center">Carregando...</TableCell>
                            </TableRow>
                        ) : (
                            sightings.map((sighting) => (
                                <TableRow key={sighting.id}>
                                    <TableCell>
                                        <Badge variant="secondary">{sighting.plate}</Badge>
                                    </TableCell>
                                    <TableCell>{sighting.camera.name}</TableCell>
                                    <TableCell className="text-right">{formatTimestamp(sighting.timestamp)}</TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
    );
}