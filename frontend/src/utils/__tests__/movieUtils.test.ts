/**
 * @fileoverview Unit tests for movie utilities
 * 
 * Tests the core utility functions for movie data validation,
 * filtering, sorting, and manipulation.
 */

import { describe, it, expect } from 'vitest';
import type { RecordType } from '../../types';
import {
  isValidRecord,
  hasValidMovie,
  safeNumber,
  safeString,
  safeBoolean,
  createSearchString,
  matchesSearchQuery,
  createDateFromTimestamp,
  isRecentRelease,
  getUserRating,
  getImdbRating,
  getCustomOrder,
  getAdditionDate,
  getReleaseDate,
  isMovieReleased,
  hasValidOptions,
  matchesRewatchCriteria,
  sortCompareFunctions,
  filterPredicates
} from '../movieUtils';

// Test data
const createMockRecord = (overrides: Partial<RecordType> = {}): RecordType => ({
  id: 1,
  listId: 1,
  rating: 4,
  order: 1,
  additionDate: 1640995200, // 2022-01-01
  movie: {
    id: 101,
    title: 'Test Movie',
    titleOriginal: 'Test Movie Original',
    director: 'Test Director',
    actors: 'Actor One, Actor Two',
    imdbRating: 8.5,
    isReleased: true,
    releaseDateTimestamp: 1640995200,
    releaseDate: '2022-01-01',
    ...overrides.movie
  },
  options: {
    ultraHd: false,
    theatre: false,
    original: true,
    ignoreRewatch: false,
    ...overrides.options
  },
  ...overrides
});

describe('movieUtils', () => {
  describe('Type guards and validation', () => {
    it('should validate valid records', () => {
      const record = createMockRecord();
      expect(isValidRecord(record)).toBe(true);
    });

    it('should reject invalid records', () => {
      expect(isValidRecord(null)).toBe(false);
      expect(isValidRecord({})).toBe(false);
      expect(isValidRecord({ movie: null })).toBe(false);
      expect(isValidRecord({ movie: {}, listId: 'invalid' })).toBe(false);
    });

    it('should validate movie structure', () => {
      const record = createMockRecord();
      expect(hasValidMovie(record)).toBe(true);
      
      const invalidRecord = createMockRecord({ movie: null as any });
      expect(hasValidMovie(invalidRecord)).toBe(false);
    });
  });

  describe('Safe value extractors', () => {
    it('should safely extract numbers', () => {
      expect(safeNumber(42)).toBe(42);
      expect(safeNumber('42')).toBe(0);
      expect(safeNumber(null)).toBe(0);
      expect(safeNumber(undefined)).toBe(0);
      expect(safeNumber(NaN)).toBe(0);
      expect(safeNumber('invalid', 10)).toBe(10);
    });

    it('should safely extract strings', () => {
      expect(safeString('hello')).toBe('hello');
      expect(safeString(42)).toBe('');
      expect(safeString(null)).toBe('');
      expect(safeString(undefined)).toBe('');
      expect(safeString(123, 'default')).toBe('default');
    });

    it('should safely extract booleans', () => {
      expect(safeBoolean(true)).toBe(true);
      expect(safeBoolean(false)).toBe(false);
      expect(safeBoolean('true')).toBe(false);
      expect(safeBoolean(1)).toBe(false);
      expect(safeBoolean(null)).toBe(false);
      expect(safeBoolean(undefined, true)).toBe(true);
    });
  });

  describe('Search functionality', () => {
    it('should create search strings from records', () => {
      const record = createMockRecord();
      const searchString = createSearchString(record);
      expect(searchString).toContain('test movie');
      expect(searchString).toContain('test director');
      expect(searchString).toContain('actor one');
    });

    it('should match search queries', () => {
      const record = createMockRecord();
      
      expect(matchesSearchQuery(record, '')).toBe(true);
      expect(matchesSearchQuery(record, 'test')).toBe(true);
      expect(matchesSearchQuery(record, 'Test Movie')).toBe(true);
      expect(matchesSearchQuery(record, 'director')).toBe(true);
      expect(matchesSearchQuery(record, 'actor')).toBe(true);
      expect(matchesSearchQuery(record, 'nonexistent')).toBe(false);
    });
  });

  describe('Date handling', () => {
    it('should create dates from timestamps', () => {
      const timestamp = 1640995200; // 2022-01-01
      const date = createDateFromTimestamp(timestamp);
      expect(date).toBeInstanceOf(Date);
      expect(date?.getFullYear()).toBe(2022);
      
      expect(createDateFromTimestamp(0)).toBeNull();
      expect(createDateFromTimestamp('invalid')).toBeNull();
      expect(createDateFromTimestamp(-1)).toBeNull();
    });

    it('should check for recent releases', () => {
      const now = Date.now() / 1000;
      const threeMonthsAgo = now - (3 * 30 * 24 * 60 * 60);
      const oneYearAgo = now - (365 * 24 * 60 * 60);
      
      expect(isRecentRelease(now)).toBe(true);
      expect(isRecentRelease(threeMonthsAgo)).toBe(true);
      expect(isRecentRelease(oneYearAgo)).toBe(false);
      expect(isRecentRelease(0)).toBe(false);
    });
  });

  describe('Data extractors', () => {
    it('should extract user ratings', () => {
      const record = createMockRecord({ rating: 5 });
      expect(getUserRating(record)).toBe(5);
      
      const invalidRecord = createMockRecord({ rating: 'invalid' as any });
      expect(getUserRating(invalidRecord)).toBe(0);
    });

    it('should extract IMDB ratings', () => {
      const record = createMockRecord();
      expect(getImdbRating(record)).toBe(8.5);
      
      const invalidRecord = createMockRecord({ movie: { ...record.movie, imdbRating: 'invalid' as any } });
      expect(getImdbRating(invalidRecord)).toBe(0);
    });
  });

  describe('Rewatch criteria', () => {
    it('should match rewatch criteria correctly', () => {
      const rewatchRecord = createMockRecord({
        rating: 5,
        options: { ultraHd: false, theatre: false, original: false, ignoreRewatch: false }
      });
      expect(matchesRewatchCriteria(rewatchRecord)).toBe(true);

      const nonRewatchRecord = createMockRecord({ rating: 3 });
      expect(matchesRewatchCriteria(nonRewatchRecord)).toBe(false);

      const ignoredRecord = createMockRecord({
        rating: 5,
        options: { ultraHd: false, theatre: false, original: false, ignoreRewatch: true }
      });
      expect(matchesRewatchCriteria(ignoredRecord)).toBe(false);
    });
  });

  describe('Sort comparison functions', () => {
    it('should sort by addition date correctly', () => {
      const record1 = createMockRecord({ additionDate: 1000 });
      const record2 = createMockRecord({ additionDate: 2000 });
      
      // Should be descending (newer first)
      expect(sortCompareFunctions.byAdditionDate(record1, record2)).toBeGreaterThan(0);
      expect(sortCompareFunctions.byAdditionDate(record2, record1)).toBeLessThan(0);
    });

    it('should sort by custom order correctly', () => {
      const record1 = createMockRecord({ order: 1 });
      const record2 = createMockRecord({ order: 2 });
      
      // Should be ascending (lower first)
      expect(sortCompareFunctions.byCustomOrder(record1, record2)).toBeLessThan(0);
      expect(sortCompareFunctions.byCustomOrder(record2, record1)).toBeGreaterThan(0);
    });

    it('should sort by rating correctly', () => {
      const record1 = createMockRecord({ rating: 3 });
      const record2 = createMockRecord({ rating: 5 });
      
      // Should be descending (higher first)
      expect(sortCompareFunctions.byUserRating(record1, record2)).toBeGreaterThan(0);
      expect(sortCompareFunctions.byUserRating(record2, record1)).toBeLessThan(0);
    });
  });

  describe('Filter predicates', () => {
    it('should filter by list ID', () => {
      const record = createMockRecord({ listId: 1 });
      
      expect(filterPredicates.byListId(1)(record)).toBe(true);
      expect(filterPredicates.byListId(2)(record)).toBe(false);
    });

    it('should filter by search query', () => {
      const record = createMockRecord();
      
      expect(filterPredicates.bySearchQuery('test')(record)).toBe(true);
      expect(filterPredicates.bySearchQuery('nonexistent')(record)).toBe(false);
      expect(filterPredicates.bySearchQuery('')(record)).toBe(true);
    });

    it('should filter for rewatch only on watched list', () => {
      const rewatchRecord = createMockRecord({
        rating: 5,
        options: { ultraHd: false, theatre: false, original: false, ignoreRewatch: false }
      });
      const normalRecord = createMockRecord({ rating: 3 });
      
      // Should apply filter only on list 1 (watched)
      expect(filterPredicates.forRewatch(1)(rewatchRecord)).toBe(true);
      expect(filterPredicates.forRewatch(1)(normalRecord)).toBe(false);
      expect(filterPredicates.forRewatch(2)(normalRecord)).toBe(true); // No filter on to-watch list
    });
  });
});