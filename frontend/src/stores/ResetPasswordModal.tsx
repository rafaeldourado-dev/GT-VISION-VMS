import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Modal, TextInput, Button, Group } from '@mantine/core';
import { useUserStore } from '../../stores/userStore';

const passwordSchema = z
  .object({
    newPassword: z.string().min(8, 'A senha deve ter no mínimo 8 caracteres'),
    confirmPassword: z.string(),
  })
  .refine((data) => data.newPassword === data.confirmPassword, {
    message: 'As senhas não coincidem',
    path: ['confirmPassword'],
  });

type PasswordFormData = z.infer<typeof passwordSchema>;

interface ResetPasswordModalProps {
  opened: boolean;
  onClose: () => void;
  userId: number | null;
}

export const ResetPasswordModal: React.FC<ResetPasswordModalProps> = ({
  opened,
  onClose,
  userId,
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<PasswordFormData>({
    resolver: zodResolver(passwordSchema),
  });
  const resetPassword = useUserStore((state) => state.resetPassword);

  const onSubmit = async (data: PasswordFormData) => {
    if (!userId) return;
    const success = await resetPassword(userId, data.newPassword);
    if (success) {
      handleClose();
    }
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  return (
    <Modal opened={opened} onClose={handleClose} title="Redefinir Senha" centered>
      <form onSubmit={handleSubmit(onSubmit)}>
        <TextInput
          label="Nova Senha"
          type="password"
          placeholder="********"
          error={errors.newPassword?.message}
          {...register('newPassword')}
          mb="md"
        />
        <TextInput
          label="Confirmar Nova Senha"
          type="password"
          placeholder="********"
          error={errors.confirmPassword?.message}
          {...register('confirmPassword')}
          mb="md"
        />
        <Group justify="flex-end" mt="lg">
          <Button variant="default" onClick={handleClose}>Cancelar</Button>
          <Button type="submit" loading={isSubmitting}>Salvar Senha</Button>
        </Group>
      </form>
    </Modal>
  );
};