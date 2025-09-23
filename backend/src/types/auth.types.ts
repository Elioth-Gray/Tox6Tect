import { Role } from '@prisma/client';

export type TToken = {
  id: string;
  email: string;
  username: string;
  avatar: string;
  role: Role;
};
