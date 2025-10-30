import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Paper,
  TextInput,
  PasswordInput,
  Button,
  Title,
  Text,
  Container,
  Group,
} from '@mantine/core';
import { useAuthStore } from '../stores/authStore';
import { useLocation, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { authService } from '../services/api';

const passwordSchema = z
  .object({
    currentPassword: z.string().min(1, 'A senha atual é obrigatória'),
    newPassword: z.string().min(8, 'A nova senha deve ter no mínimo 8 caracteres'),
    confirmPassword: z.string(),
  })
  .refine((data) => data.newPassword === data.confirmPassword, {
    message: 'As senhas não coincidem',
    path: ['confirmPassword'],
  });

type PasswordFormData = z.infer<typeof passwordSchema>;

const ForcePasswordChangePage: React.FC = () => {
  const { updateOwnPassword, user } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation() as any;
  const passedEmail: string | undefined = location?.state?.email;
  const passedOldPassword: string | undefined = location?.state?.oldPassword;

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<PasswordFormData>({
    resolver: zodResolver(passwordSchema),
  });

  const onSubmit = async (data: PasswordFormData) => {
    try {
      if (passedEmail && passedOldPassword) {
        // Fluxo inicial sem JWT
        await authService.forcePasswordChangeInitial(
          passedEmail,
          data.currentPassword || passedOldPassword,
          data.newPassword
        );
      } else {
        // Fluxo autenticado (usuário já tem token)
        const success = await updateOwnPassword(data.currentPassword, data.newPassword);
        if (!success) return;
      }
      toast.success('Senha alterada com sucesso! Faça login novamente.');
      navigate('/login');
    } catch (e: any) {
      toast.error(e.response?.data?.detail || 'Erro ao alterar a senha.');
    }
  };

  return (
    <Container size={420} my={40}>
      <Title ta="center">Alteração de Senha Obrigatória</Title>
      <Text c="dimmed" size="sm" ta="center" mt={5}>
        {user?.full_name ? (
          <>Olá, {user.full_name}! Por segurança, você precisa definir uma nova senha.</>
        ) : (
          <>Por segurança, você precisa definir uma nova senha para continuar.</>
        )}
      </Text>

      <Paper withBorder shadow="md" p={30} mt={30} radius="md">
        <form onSubmit={handleSubmit(onSubmit)}>
          <PasswordInput
            label="Senha Atual"
            placeholder="A senha temporária fornecida"
            required
            error={errors.currentPassword?.message}
            {...register('currentPassword')}
            mb="md"
          />
          <PasswordInput
            label="Nova Senha"
            placeholder="********"
            required
            error={errors.newPassword?.message}
            {...register('newPassword')}
            mb="md"
          />
          <PasswordInput
            label="Confirmar Nova Senha"
            placeholder="********"
            required
            error={errors.confirmPassword?.message}
            {...register('confirmPassword')}
            mb="lg"
          />
          <Button type="submit" fullWidth mt="xl" loading={isSubmitting}>
            Definir Nova Senha
          </Button>
        </form>
      </Paper>
    </Container>
  );
};

export default ForcePasswordChangePage;