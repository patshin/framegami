export type Locale = 'zh' | 'en';
export type Model = 'chatgpt' | 'gemini' | 'flux';
export type Localized = Record<Locale,string>;
export interface ExampleEvidence {
  styleId: string;
  model: Model;
  lang: Locale;
  requestKind: 'image-edit';
  singleIndependentOutput: boolean;
  path: string;
  originalSha256: string;
  outputSha256: string;
  promptSha256: string;
  promptPath: string;
  environment: string;
  promptVersion: string;
  date: string;
  accepted: boolean;
  review: Record<'identity'|'composition'|'style'|'wholeScene'|'anatomy',boolean>;
  reviewer: string;
}
export interface Style {
  id:string; category:string; family:string; name:Localized; technique:Localized;
  avoid:Localized; limits:Localized; aliases:string[]; sources:string[];
  status:'draft'|'exampled'; version:string; examples:ExampleEvidence[];
  tags:string[]; preservation:'structure'|'reinterpret'; order:number;
  testedModels:Model[]; modelStatus:Record<Model,'untested'|'exampled'>;
}
