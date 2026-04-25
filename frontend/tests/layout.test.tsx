import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { Sidebar } from '../src/components/layout/Sidebar';
import { BrowserRouter } from 'react-router-dom';

describe('Layout', () => {
  it('renders sidebar with navigation items', () => {
    const { getByText } = render(<BrowserRouter><Sidebar /></BrowserRouter>);
    expect(getByText('Vanguard')).toBeDefined();
    expect(getByText('Dashboard')).toBeDefined();
  });
});
