/**
 * API client for StakeholderSim backend
 */

export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Scenario {
  id: string;
  name: string;
  description: string | null;
  persona_name: string;
  persona_title: string;
  persona_background: string | null;
  is_practice: boolean;
  max_turns: number;
}

export interface Message {
  id: string;
  role: 'student' | 'stakeholder';
  content: string;
  created_at: string;
}

export interface Conversation {
  id: string;
  scenario_id: string;
  persona_name: string;
  persona_title: string;
  mode: 'practice' | 'graded';
  status: 'in_progress' | 'completed' | 'abandoned';
  context: string;
  turn_count: number;
  started_at: string;
  completed_at: string | null;
  violation_count: number;
  violation_log: ViolationEntry[] | null;
  ended_at: string | null;
  total_active_seconds: number | null;
  messages: Message[];
}

export interface ViolationEntry {
  violation_number: number;
  timestamp: string;
  turn_number: number;
}

export interface ConversationListItem {
  id: string;
  scenario_id: string;
  persona_name: string;
  mode: string;
  status: string;
  turn_count: number;
  started_at: string;
  completed_at: string | null;
  score: number | null;
}

export interface SendMessageResponse {
  student_message: Message;
  stakeholder_message: Message;
  conversation_status: string;
  turn_count: number;
  should_end: boolean;
}

export interface EndConversationResponse {
  id: string;
  status: string;
  turn_count: number;
  completed_at: string;
  final_message: Message | null;
}

export interface CriterionScore {
  score: number;
  max_score: number;
  evidence: string;
  feedback: string;
}

export interface Grade {
  id: string;
  conversation_id: string;
  rubric_id: string;
  criteria_scores: Record<string, CriterionScore>;
  total_score: number;
  max_score: number;
  overall_feedback: string;
  strengths: string[];
  areas_for_improvement: string[];
  ai_confidence: number | null;
  graded_by: 'ai' | 'instructor';
  instructor_override: boolean;
  override_reason: string | null;
  graded_at: string;
  needs_review: boolean;
  violation_count: number;
  violation_log: ViolationEntry[] | null;
  total_active_seconds: number | null;
  ended_at: string | null;
}

// Dashboard types
export interface StudentStats {
  total_conversations: number;
  completed_conversations: number;
  practice_sessions: number;
  graded_sessions: number;
  average_score: number | null;
  best_score: number | null;
  total_improvement: number | null;
}

export interface RecentConversation {
  id: string;
  persona_name: string;
  status: string;
  score: number | null;
  started_at: string;
  completed_at: string | null;
}

export interface ProgressPoint {
  date: string;
  score: number;
  conversation_id: string;
  persona_name: string;
}

export interface StudentDashboard {
  stats: StudentStats;
  recent_conversations: RecentConversation[];
  progress_history: ProgressPoint[];
  recommended_scenario: string | null;
}

export interface StudentSummary {
  id: string;
  name: string;
  email: string;
  total_conversations: number;
  average_score: number | null;
  last_active: string | null;
  needs_attention: boolean;
}

export interface ClassStats {
  total_students: number;
  active_students: number;
  total_conversations: number;
  total_graded: number;
  average_score: number | null;
  score_distribution: Record<string, number>;
  common_struggles: string[];
}

export interface GradeForReview {
  id: string;
  conversation_id: string;
  student_name: string;
  persona_name: string;
  score: number;
  ai_confidence: number;
  graded_at: string;
}

export interface InstructorDashboard {
  class_stats: ClassStats;
  recent_activity: RecentConversation[];
  students: StudentSummary[];
  grades_needing_review: GradeForReview[];
}

// Assignment types
export interface AssignmentListItem {
  id: string;
  title: string;
  scenario_name: string;
  persona_name: string;
  due_date: string | null;
  max_attempts: number;
  is_active: boolean;
  total_submissions: number;
  graded_submissions: number;
}

export interface StudentAssignment {
  id: string;
  title: string;
  instructions: string | null;
  scenario_id: string;
  scenario_name: string;
  persona_name: string;
  persona_title: string;
  due_date: string | null;
  max_attempts: number;
  attempts_used: number;
  best_score: number | null;
  can_attempt: boolean;
}

export interface AssignmentSubmission {
  id: string;
  conversation_id: string;
  student_id: string;
  student_name: string;
  started_at: string;
  completed_at: string | null;
  score: number | null;
  status: string;
}

export interface AssignmentCreate {
  title: string;
  instructions?: string;
  scenario_id: string;
  course_id: string;
  due_date?: string;
  max_attempts?: number;
  is_active?: boolean;
}

export interface AssignmentResponse {
  id: string;
  title: string;
  instructions: string | null;
  scenario_id: string;
  course_id: string;
  scenario_name: string;
  persona_name: string;
  due_date: string | null;
  max_attempts: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Persona types
export interface PersonaListItem {
  id: string;
  name: string;
  title: string;
  is_active: boolean;
  created_at: string;
}

export interface PersonaResponse {
  id: string;
  course_id: string | null;
  name: string;
  title: string;
  background: string | null;
  personality: string | null;
  concerns: string[] | null;
  required_questions: string[] | null;
  is_active: boolean;
  created_at: string;
}

export interface PersonaCreate {
  course_id: string;
  name: string;
  title: string;
  background?: string;
  personality?: string;
  concerns?: string[];
  required_questions?: string[];
}

// Rubric types
export interface CriterionSchema {
  name: string;
  display_name: string;
  description: string;
  max_points: number;
  scoring_guide?: Record<string, string>;
}

export interface RubricListItem {
  id: string;
  name: string;
  total_points: number;
  criteria_count: number;
  created_at: string;
}

export interface RubricResponse {
  id: string;
  course_id: string | null;
  name: string;
  criteria: CriterionSchema[];
  total_points: number;
  created_at: string;
}

export interface RubricCreate {
  course_id: string;
  name: string;
  criteria: CriterionSchema[];
}

export interface RubricDraft {
  name: string;
  criteria: CriterionSchema[];
}

export interface RubricChatMessage {
  role: string;
  content: string;
}

export interface RubricChatResponse {
  reply: string;
  rubric_draft: RubricDraft | null;
}

export interface MaterialUploadResponse {
  extracted_text: string;
  filename: string;
  pages: number | null;
}

// Scenario types (instructor CRUD)
export interface ScenarioListItem {
  id: string;
  name: string;
  persona_name: string;
  rubric_name: string;
  is_practice: boolean;
  max_turns: number;
  created_at: string;
}

export interface ScenarioResponse {
  id: string;
  course_id: string | null;
  name: string;
  description: string | null;
  persona_id: string;
  rubric_id: string;
  persona_name: string;
  rubric_name: string;
  is_practice: boolean;
  max_turns: number;
  created_at: string;
}

export interface ScenarioCreate {
  course_id: string;
  name: string;
  description?: string;
  persona_id: string;
  rubric_id: string;
  is_practice?: boolean;
  max_turns?: number;
}

// Quiz types
export interface QuizListItem {
  id: string;
  title: string;
  due_date: string | null;
  max_attempts: number;
  is_active: boolean;
  question_count: number;
  total_points: number;
  total_attempts: number;
}

export interface StudentQuiz {
  id: string;
  title: string;
  description: string | null;
  due_date: string | null;
  time_limit_minutes: number | null;
  max_attempts: number;
  attempts_used: number;
  best_score: number | null;
  max_score: number;
  can_attempt: boolean;
  question_count: number;
}

export interface StudentQuestionView {
  id: string;
  question_type: string;
  question_text: string;
  options: string[] | null;
  points: number;
  order_index: number;
}

export interface QuestionCreate {
  question_type: string;
  question_text: string;
  options?: string[];
  correct_answer: string;
  acceptable_answers?: string[];
  points?: number;
  order_index?: number;
}

export interface QuizCreate {
  title: string;
  description?: string;
  course_id: string;
  time_limit_minutes?: number;
  max_attempts?: number;
  due_date?: string;
  is_active?: boolean;
  show_answers_after_submit?: boolean;
  questions: QuestionCreate[];
}

export interface QuestionResponse {
  id: string;
  question_type: string;
  question_text: string;
  options: string[] | null;
  correct_answer: string;
  acceptable_answers: string[] | null;
  points: number;
  order_index: number;
}

export interface QuizDetailResponse {
  id: string;
  title: string;
  description: string | null;
  course_id: string;
  time_limit_minutes: number | null;
  max_attempts: number;
  due_date: string | null;
  is_active: boolean;
  show_answers_after_submit: boolean;
  question_count: number;
  total_points: number;
  created_at: string;
  questions: QuestionResponse[];
}

export interface AnswerSubmit {
  question_id: string;
  student_answer: string;
}

export interface AnswerResult {
  question_id: string;
  question_text: string;
  question_type: string;
  student_answer: string | null;
  correct_answer: string | null;
  is_correct: boolean | null;
  points_awarded: number;
  points_possible: number;
  needs_review: boolean;
}

export interface AttemptResponse {
  id: string;
  quiz_id: string;
  score: number;
  max_score: number;
  started_at: string;
  submitted_at: string;
  answers: AnswerResult[];
}

export interface AttemptListItem {
  id: string;
  student_id: string;
  student_name: string;
  score: number | null;
  max_score: number | null;
  started_at: string;
  submitted_at: string | null;
  is_submitted: boolean;
  needs_review: boolean;
}

// Auth types
export interface AuthUser {
  id: string;
  email: string;
  name: string;
  role: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: AuthUser;
}

class ApiClient {
  private getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('auth_token');
  }

  private setToken(token: string) {
    localStorage.setItem('auth_token', token);
  }

  private clearToken() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
  }

  getUser(): AuthUser | null {
    if (typeof window === 'undefined') return null;
    const raw = localStorage.getItem('auth_user');
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch {
      return null;
    }
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  private async fetch<T>(
    endpoint: string,
    options: RequestInit = {},
    skipAuthRedirect: boolean = false
  ): Promise<T> {
    const url = `${API_BASE}${endpoint}`;
    const token = this.getToken();

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> || {}),
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (response.status === 401 && !skipAuthRedirect) {
      this.clearToken();
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
      throw new Error('Session expired. Please log in again.');
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Auth
  async signup(email: string, password: string, name: string, role: string = 'student'): Promise<TokenResponse> {
    const data = await this.fetch<TokenResponse>('/api/v1/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ email, password, name, role }),
    }, true);
    this.setToken(data.access_token);
    localStorage.setItem('auth_user', JSON.stringify(data.user));
    return data;
  }

  async login(email: string, password: string): Promise<TokenResponse> {
    const data = await this.fetch<TokenResponse>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }, true);
    this.setToken(data.access_token);
    localStorage.setItem('auth_user', JSON.stringify(data.user));
    return data;
  }

  logout() {
    this.clearToken();
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  }

  async getMe(): Promise<AuthUser> {
    return this.fetch<AuthUser>('/api/v1/auth/me');
  }

  // Scenarios
  async getScenarios(): Promise<Scenario[]> {
    return this.fetch<Scenario[]>('/api/v1/conversations/scenarios');
  }

  // Conversations
  async startConversation(
    scenarioId: string,
    context: string,
    assignmentId?: string
  ): Promise<Conversation> {
    return this.fetch<Conversation>('/api/v1/conversations', {
      method: 'POST',
      body: JSON.stringify({
        scenario_id: scenarioId,
        context,
        assignment_id: assignmentId,
      }),
    });
  }

  async getConversation(conversationId: string): Promise<Conversation> {
    return this.fetch<Conversation>(`/api/v1/conversations/${conversationId}`);
  }

  async listConversations(
    limit: number = 20,
    offset: number = 0
  ): Promise<ConversationListItem[]> {
    return this.fetch<ConversationListItem[]>(
      `/api/v1/conversations?limit=${limit}&offset=${offset}`
    );
  }

  async sendMessage(
    conversationId: string,
    content: string
  ): Promise<SendMessageResponse> {
    return this.fetch<SendMessageResponse>(
      `/api/v1/conversations/${conversationId}/messages`,
      {
        method: 'POST',
        body: JSON.stringify({ content }),
      }
    );
  }

  async endConversation(
    conversationId: string,
    totalActiveSeconds?: number
  ): Promise<EndConversationResponse> {
    return this.fetch<EndConversationResponse>(
      `/api/v1/conversations/${conversationId}/end`,
      {
        method: 'POST',
        body: JSON.stringify({
          total_active_seconds: totalActiveSeconds ?? null,
        }),
      }
    );
  }

  async logViolation(
    conversationId: string,
    violationNumber: number,
    timestamp: string,
    turnNumber: number
  ): Promise<{ violation_count: number; violation_log: ViolationEntry[] }> {
    return this.fetch(`/api/v1/conversations/${conversationId}/violations`, {
      method: 'POST',
      body: JSON.stringify({
        violation_number: violationNumber,
        timestamp,
        turn_number: turnNumber,
      }),
    });
  }

  // Health
  async healthCheck(): Promise<{ status: string; service: string }> {
    return this.fetch('/health');
  }

  // Grading
  async getGrade(conversationId: string): Promise<Grade> {
    return this.fetch<Grade>(`/api/v1/grades/conversations/${conversationId}`);
  }

  async triggerGrading(conversationId: string, force: boolean = false): Promise<Grade> {
    return this.fetch<Grade>(
      `/api/v1/grades/conversations/${conversationId}/grade`,
      {
        method: 'POST',
        body: JSON.stringify({ force }),
      }
    );
  }

  // Dashboard
  async getStudentDashboard(): Promise<StudentDashboard> {
    return this.fetch<StudentDashboard>('/api/v1/dashboard/student');
  }

  async getInstructorDashboard(): Promise<InstructorDashboard> {
    return this.fetch<InstructorDashboard>('/api/v1/dashboard/instructor');
  }

  // Assignments
  async listAssignments(courseId?: string, activeOnly: boolean = false): Promise<AssignmentListItem[]> {
    let url = '/api/v1/assignments';
    const params: string[] = [];
    if (courseId) params.push(`course_id=${courseId}`);
    if (activeOnly) params.push('active_only=true');
    if (params.length > 0) url += '?' + params.join('&');
    return this.fetch<AssignmentListItem[]>(url);
  }

  async getStudentAssignments(): Promise<StudentAssignment[]> {
    return this.fetch<StudentAssignment[]>('/api/v1/assignments/student');
  }

  async getAssignment(assignmentId: string): Promise<AssignmentResponse> {
    return this.fetch<AssignmentResponse>(`/api/v1/assignments/${assignmentId}`);
  }

  async createAssignment(data: AssignmentCreate): Promise<AssignmentResponse> {
    return this.fetch<AssignmentResponse>('/api/v1/assignments', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateAssignment(assignmentId: string, data: Partial<AssignmentCreate>): Promise<AssignmentResponse> {
    return this.fetch<AssignmentResponse>(`/api/v1/assignments/${assignmentId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteAssignment(assignmentId: string): Promise<void> {
    await this.fetch(`/api/v1/assignments/${assignmentId}`, {
      method: 'DELETE',
    });
  }

  async getAssignmentSubmissions(assignmentId: string): Promise<AssignmentSubmission[]> {
    return this.fetch<AssignmentSubmission[]>(`/api/v1/assignments/${assignmentId}/submissions`);
  }

  // Personas
  async listPersonas(courseId?: string): Promise<PersonaListItem[]> {
    let url = '/api/v1/personas';
    if (courseId) url += `?course_id=${courseId}`;
    return this.fetch<PersonaListItem[]>(url);
  }

  async getPersona(personaId: string): Promise<PersonaResponse> {
    return this.fetch<PersonaResponse>(`/api/v1/personas/${personaId}`);
  }

  async createPersona(data: PersonaCreate): Promise<PersonaResponse> {
    return this.fetch<PersonaResponse>('/api/v1/personas', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updatePersona(personaId: string, data: Partial<PersonaCreate>): Promise<PersonaResponse> {
    return this.fetch<PersonaResponse>(`/api/v1/personas/${personaId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deletePersona(personaId: string): Promise<void> {
    await this.fetch(`/api/v1/personas/${personaId}`, { method: 'DELETE' });
  }

  // Rubrics
  async listRubrics(): Promise<RubricListItem[]> {
    return this.fetch<RubricListItem[]>('/api/v1/rubrics');
  }

  async getRubric(rubricId: string): Promise<RubricResponse> {
    return this.fetch<RubricResponse>(`/api/v1/rubrics/${rubricId}`);
  }

  async createRubric(data: RubricCreate): Promise<RubricResponse> {
    return this.fetch<RubricResponse>('/api/v1/rubrics', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateRubric(rubricId: string, data: Partial<RubricCreate>): Promise<RubricResponse> {
    return this.fetch<RubricResponse>(`/api/v1/rubrics/${rubricId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteRubric(rubricId: string): Promise<void> {
    await this.fetch(`/api/v1/rubrics/${rubricId}`, { method: 'DELETE' });
  }

  async uploadRubricMaterial(file: File): Promise<MaterialUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    const url = `${API_BASE}/api/v1/rubrics/upload-material`;
    const token = this.getToken();
    const headers: Record<string, string> = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  async rubricChat(messages: RubricChatMessage[], materialsText: string): Promise<RubricChatResponse> {
    return this.fetch<RubricChatResponse>('/api/v1/rubrics/chat', {
      method: 'POST',
      body: JSON.stringify({ messages, materials_text: materialsText }),
    });
  }

  // Scenarios (instructor CRUD)
  async listScenariosAdmin(): Promise<ScenarioListItem[]> {
    return this.fetch<ScenarioListItem[]>('/api/v1/scenarios');
  }

  async getScenarioAdmin(scenarioId: string): Promise<ScenarioResponse> {
    return this.fetch<ScenarioResponse>(`/api/v1/scenarios/${scenarioId}`);
  }

  async createScenario(data: ScenarioCreate): Promise<ScenarioResponse> {
    return this.fetch<ScenarioResponse>('/api/v1/scenarios', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateScenario(scenarioId: string, data: Partial<ScenarioCreate>): Promise<ScenarioResponse> {
    return this.fetch<ScenarioResponse>(`/api/v1/scenarios/${scenarioId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteScenario(scenarioId: string): Promise<void> {
    await this.fetch(`/api/v1/scenarios/${scenarioId}`, { method: 'DELETE' });
  }

  // Quizzes (instructor)
  async listQuizzesAdmin(courseId?: string, activeOnly: boolean = false): Promise<QuizListItem[]> {
    let url = '/api/v1/quizzes';
    const params: string[] = [];
    if (courseId) params.push(`course_id=${courseId}`);
    if (activeOnly) params.push('active_only=true');
    if (params.length > 0) url += '?' + params.join('&');
    return this.fetch<QuizListItem[]>(url);
  }

  async getQuizAdmin(quizId: string): Promise<QuizDetailResponse> {
    return this.fetch<QuizDetailResponse>(`/api/v1/quizzes/${quizId}`);
  }

  async createQuiz(data: QuizCreate): Promise<QuizDetailResponse> {
    return this.fetch<QuizDetailResponse>('/api/v1/quizzes', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateQuiz(quizId: string, data: Partial<QuizCreate>): Promise<QuizDetailResponse> {
    return this.fetch<QuizDetailResponse>(`/api/v1/quizzes/${quizId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteQuiz(quizId: string): Promise<void> {
    await this.fetch(`/api/v1/quizzes/${quizId}`, { method: 'DELETE' });
  }

  async getQuizResults(quizId: string): Promise<AttemptListItem[]> {
    return this.fetch<AttemptListItem[]>(`/api/v1/quizzes/${quizId}/results`);
  }

  async gradeAnswer(answerId: string, data: { is_correct: boolean; points_awarded: number }): Promise<void> {
    await this.fetch(`/api/v1/quizzes/answers/${answerId}/grade`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // Quizzes (student)
  async getStudentQuizzes(): Promise<StudentQuiz[]> {
    return this.fetch<StudentQuiz[]>('/api/v1/quizzes/student');
  }

  async getMyAttempts(quizId: string): Promise<AttemptResponse[]> {
    return this.fetch<AttemptResponse[]>(`/api/v1/quizzes/${quizId}/my-attempts`);
  }

  async takeQuiz(quizId: string): Promise<StudentQuestionView[]> {
    return this.fetch<StudentQuestionView[]>(`/api/v1/quizzes/${quizId}/take`);
  }

  async startQuizAttempt(quizId: string): Promise<{ attempt_id: string; started_at: string }> {
    return this.fetch(`/api/v1/quizzes/${quizId}/start`, { method: 'POST' });
  }

  async submitQuizAttempt(attemptId: string, data: { answers: AnswerSubmit[] }): Promise<AttemptResponse> {
    return this.fetch<AttemptResponse>(`/api/v1/quizzes/attempts/${attemptId}/submit`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

export const api = new ApiClient();
