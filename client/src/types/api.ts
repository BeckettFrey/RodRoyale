export interface User {
  _id: string;
  username: string;
  email: string;
  bio?: string;
  followers: string[];
  following: string[];
}

export interface Location {
  lat: number;
  lng: number;
  city?: string;
  state?: string;
  country?: string;
}

export interface Catch {
  _id: string;
  user_id: string;
  species: string;
  weight: number;
  photo_url: string;
  location: Location;
  shared_with_followers: boolean;
  created_at: string;
}

export interface Pin {
  id: string;
  user_id: string;
  catch_id: string;
  location: Location;
  visibility: 'private' | 'mutuals' | 'public';
  catch_info?: Catch;
  owner_info?: User;
}

export interface CreateUserRequest {
  username: string;
  email: string;
  bio?: string;
}

export interface UpdateUserRequest {
  username?: string;
  email?: string;
  bio?: string;
}

export interface CreateCatchRequest {
  species: string;
  weight: number;
  photo_url: string;
  location: Location;
  shared_with_followers: boolean;
}

export interface CreatePinRequest {
  catch_id: string;
  location: Location;
  visibility: 'private' | 'mutuals' | 'public';
}

// Leaderboard types
export interface UserStats {
  total_catches: number;
  biggest_catch_month: number;
  biggest_catch_species: string;
  catches_this_month: number;
  best_average_month: number;
}

export interface LeaderboardUser {
  _id: string;
  username: string;
  rank: number;
  is_current_user: boolean;
  total_catches: number;
  biggest_catch_month: number;
  catches_this_month: number;
  best_average_month: number;
}

export interface LeaderboardResponse {
  current_user_rank: number;
  total_users: number;
  leaderboard: LeaderboardUser[];
}

export type LeaderboardMetric = 'biggest_catch_month' | 'catches_this_month' | 'best_average_month';
