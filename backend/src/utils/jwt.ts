import jwt from 'jsonwebtoken';
import { TToken } from '../types/auth.types';
import { JWT_SECRET } from './env';

export const generateToken = (data: TToken) => {
  const tokenData: TToken = data;

  const SECRET = JWT_SECRET;
  if (!SECRET) {
    throw new Error('JWT_SECRET is not defined');
  }

  const token = jwt.sign(
    {
      id: tokenData.id,
      email: tokenData.email,
      username: tokenData.username,
      avatar: tokenData.avatar,
      role: tokenData.role,
    },
    SECRET,
    { expiresIn: '1h' },
  );

  return token;
};

export const decodeToken = (token: string): TToken | null => {
  try {
    const SECRET = JWT_SECRET;
    if (!SECRET) {
      throw new Error('JWT_SECRET is not defined');
    }

    const decoded = jwt.verify(token, SECRET);

    if (
      typeof decoded === 'object' &&
      decoded.id &&
      decoded.email &&
      decoded.username &&
      decoded.avatar &&
      decoded.role
    ) {
      return {
        id: decoded.id,
        email: decoded.email,
        username: decoded.username,
        avatar: decoded.avatar,
        role: decoded.role,
      };
    }

    return null;
  } catch (err) {
    return null;
  }
};
