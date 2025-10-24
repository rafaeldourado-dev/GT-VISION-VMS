import React, { useEffect, useMemo } from 'react';
import { useAuditLogStore } from '../stores/auditLogStore';
import { useUserStore } from '../stores/userStore';
import { Table, Title, Box, Text, Pagination, LoadingOverlay, Grid, Select, Button } from '@mantine/core';
import { DatePickerInput } from '@mantine/dates';
import { IconFilter, IconX } from '@tabler/icons-react';

const AuditLogPage: React.FC = () => {
  const {
    logs,
    isLoading,
    totalLogs,
    currentPage,
    itemsPerPage,
    fetchLogs,
    setCurrentPage,
    filters,
    setFilters,
  } = useAuditLogStore();

  const { users, fetchUsers } = useUserStore();

  useEffect(() => {
    fetchUsers(); // Carrega os usuários para o filtro de ator
  }, [fetchUsers]);

  useEffect(() => {
    fetchLogs();
  }, [currentPage, fetchLogs, filters]);

  const userOptions = useMemo(() => 
    users.map(user => ({ value: user.id.toString(), label: user.full_name })),
  [users]);

  const actionOptions = [
    { value: 'USER_CREATED', label: 'Criação de Usuário' },
    { value: 'PASSWORD_RESET', label: 'Reset de Senha' },
  ];

  const handleClearFilters = () => {
    setFilters({ actor_id: null, action: null, date_range: [null, null] });
  };

  const totalPages = Math.ceil(totalLogs / itemsPerPage);

  const rows = logs.map((log) => (
    <Table.Tr key={log.id}>
      <Table.Td>{new Date(log.timestamp).toLocaleString()}</Table.Td>
      <Table.Td>
        <Text size="sm">{log.actor.full_name}</Text>
        <Text size="xs" c="dimmed">{log.actor.email}</Text>
      </Table.Td>
      <Table.Td>
        <Text fw={500}>{log.action}</Text>
      </Table.Td>
      <Table.Td>
        {log.target_type && log.target_id ? `${log.target_type} (ID: ${log.target_id})` : 'N/A'}
      </Table.Td>
      <Table.Td>
        <Text size="sm" style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
          {log.details}
        </Text>
      </Table.Td>
    </Table.Tr>
  ));

  return (
    <Box>
      <Box mb="lg">
        <Title order={2}>Log de Auditoria</Title>
        <Text c="dimmed">Filtre e visualize os eventos de segurança do sistema.</Text>
      </Box>

      <Box component="form" onSubmit={(e) => e.preventDefault()} mb="xl" p="md" style={{ border: '1px solid #dee2e6', borderRadius: '4px' }}>
        <Grid align="flex-end">
          <Grid.Col span={{ base: 12, md: 3 }}>
            <Select
              label="Ator"
              placeholder="Filtrar por usuário"
              data={userOptions}
              value={filters.actor_id?.toString() || null}
              onChange={(value) => setFilters({ actor_id: value ? parseInt(value) : null })}
              clearable
            />
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 3 }}>
            <Select
              label="Ação"
              placeholder="Filtrar por ação"
              data={actionOptions}
              value={filters.action || null}
              onChange={(value) => setFilters({ action: value })}
              clearable
            />
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 4 }}>
            <DatePickerInput type="range" label="Intervalo de Datas" placeholder="Selecione as datas" value={filters.date_range || [null, null]} onChange={(value) => setFilters({ date_range: value })} clearable />
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 2 }}>
            <Button leftSection={<IconX size={16} />} variant="default" onClick={handleClearFilters} fullWidth>Limpar Filtros</Button>
          </Grid.Col>
        </Grid>
      </Box>

      <Box pos="relative">
        <LoadingOverlay visible={isLoading} zIndex={1000} overlayProps={{ radius: "sm", blur: 2 }} />
        <Table striped highlightOnHover withTableBorder withColumnBorders>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Data/Hora</Table.Th>
              <Table.Th>Ator</Table.Th>
              <Table.Th>Ação</Table.Th>
              <Table.Th>Alvo</Table.Th>
              <Table.Th>Detalhes</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>{rows.length > 0 ? rows : <Table.Tr><Table.Td colSpan={5}><Text ta="center">Nenhum log encontrado.</Text></Table.Td></Table.Tr>}</Table.Tbody>
        </Table>
      </Box>

      {totalPages > 1 && (
        <Pagination
          total={totalPages}
          value={currentPage}
          onChange={setCurrentPage}
          mt="lg"
          position="center"
        />
      )}
    </Box>
  );
};

export default AuditLogPage;