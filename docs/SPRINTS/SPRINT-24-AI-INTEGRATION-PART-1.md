# Sprint 24: AI Integration with Anthropic Claude (Part 1)

<!-- CLICKUP_LIST_ID: 901519464175 -->

**Sprint Duration:** 24/11/2026 - 08/12/2026 (2 weeks)
**Capacity:** 11/11 points (at capacity)
**Status:** Planned

---

## Sprint Goal

Integrate Anthropic Claude AI throughout the platform enabling AI chat, content generation, SEO suggestions, and usage tracking with budget controls.

---

## MoSCoW Breakdown

### Must Have (11 points - Should Have Priority)

| Story ID                                      | Title                   | Points | Status  |
| --------------------------------------------- | ----------------------- | ------ | ------- |
| [US-015](../STORIES/US-015-AI-INTEGRATION.md) | AI Integration (Part 1) | 11     | Pending |

_US-015 split: 11 points for Claude API, chat interface, content generation, and usage tracking this sprint, 2 points for SEO and alt text features in Sprint 25_

---

## Dependencies

| Story  | Depends On | Notes                           |
| ------ | ---------- | ------------------------------- |
| US-015 | US-014     | Integration framework completed |

**Dependencies satisfied:** Integration framework (Sprint 17) is complete.

---

## Implementation Order

### Week 1 (24/11 - 01/12)

1. **Claude API and Backend (Priority 1)**
   - Backend: AIProvider model
   - Backend: AIUsageLog model
   - Backend: AIConversation model
   - Backend: AIMessage model
   - Backend: AIBudget model
   - Backend: Anthropic Claude adapter
   - Backend: Usage tracking and logging
   - Backend: Budget checking middleware
   - Backend: GraphQL queries/mutations for AI
   - Backend: Rate limiting per user

**Milestone:** Claude API integrated with usage tracking and budget controls

### Week 2 (01/12 - 08/12)

2. **AI Chat Interface (Priority 2)**
   - Frontend Web: AIChat page/component
   - Frontend Web: ChatMessage component
   - Frontend Web: ChatInput component
   - Frontend Web: ConversationList sidebar
   - Frontend Web: TokenUsageIndicator
   - Frontend Web: GenerateContentButton (in page editor)
   - Frontend Web: BudgetWarning component
   - Frontend Mobile: Simplified AI chat
   - Shared UI: Chat components
   - Testing: AI integration tests with mock API

**Milestone:** AI chat operational with streaming responses

---

## Repository Breakdown

| Story  | Backend | Frontend Web | Frontend Mobile | Shared UI |
| ------ | ------- | ------------ | --------------- | --------- |
| US-015 | ✅      | ✅           | ✅              | ✅        |

**All 4 repositories** will be active this sprint.

---

## Technical Focus

### Backend

- **Claude Integration:** Anthropic API wrapper
- **Streaming Responses:** Server-sent events for real-time responses
- **Usage Tracking:** Track tokens and costs per organisation
- **Budget Controls:** Enforce monthly limits

### Frontend Web

- **Chat Interface:** Real-time AI conversation
- **Content Generation:** AI-assisted content creation
- **Streaming:** Display AI responses as they arrive

### Frontend Mobile

- **Mobile Chat:** Touch-optimised AI interface

### Shared UI

- **Chat Components:** Reusable message display

---

## Risks & Mitigations

| Risk                          | Likelihood | Impact | Mitigation                                                 |
| ----------------------------- | ---------- | ------ | ---------------------------------------------------------- |
| Claude API rate limits        | High       | High   | Implement rate limiting, queue requests                    |
| Streaming response complexity | Medium     | Medium | Use SSE or WebSockets, handle connection drops             |
| Token cost management         | High       | High   | Enforce budgets early, warn at 80%                         |
| Prompt engineering takes time | High       | Medium | Use established prompt patterns, iterate based on feedback |

---

## Acceptance Criteria Summary

### US-015: AI Integration (Part 1)

- [ ] Claude API key configured and stored securely
- [ ] AI chat interface operational
- [ ] Conversations saved and retrievable
- [ ] Token usage tracked per request
- [ ] Budget controls enforce limits
- [ ] Warnings sent at 80% budget usage
- [ ] Content generation available in page editor
- [ ] Streaming responses work in real-time
- [ ] Mobile AI chat functional

**Deferred to Sprint 25:**

- SEO suggestions
- Image alt text generation
- Code assistance features

---

## Definition of Done

- [ ] All acceptance criteria met for US-015 (Part 1)
- [ ] Unit tests pass (>80% coverage)
- [ ] Integration tests with mock Claude API pass
- [ ] Budget controls tested
- [ ] Code reviewed and merged to main
- [ ] Documentation updated
- [ ] Deployed to development environment
- [ ] QA tested
- [ ] Demo prepared

---

## Sprint Metrics

| Metric           | Target | Actual |
| ---------------- | ------ | ------ |
| Points Committed | 11     | -      |
| Points Completed | -      | -      |
| AI Features      | 3      | -      |

---

_Last Updated: 06/01/2026_
_Sprint Owner: Development Team_
