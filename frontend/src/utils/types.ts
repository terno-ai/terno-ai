export interface OrganisationFormData {
  name: string;
  subdomain: string;
}

export interface Organisation {
  id: number;
  name: string;
  subdomain: string;
  url: string;
  admin_url: string;
  owner: string;
  logo: string;
  is_active: string;
}

export interface OrganisationsResponse {
  success: boolean;
  organisations: Organisation[];
}

export interface Flow {
  id: string;
  is_pending?: boolean;
  providers?: string[];
}

export interface Response {
  status: number;
  data: {
    flows: Flow[];
  };
  meta: {
    is_authenticated: boolean;
  };
}

export interface Error {
  message: string;
  code: string;
  param: string;
}

export interface ErrorResponse {
  status: number;
  errors: Error[];
}
