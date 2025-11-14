'use client';

import { useState, useEffect } from 'react';
import { getCategories, createCategory, updateCategory, deleteCategory } from '@/lib/api';

interface Category {
  id: number;
  name: string;
  slug?: string;
}

export default function CategoryManagement() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [formData, setFormData] = useState({
    name: ''
  });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      setError(null);
      const data = await getCategories();
      setCategories(data || []);
    } catch (error: any) {
      console.error('Error loading categories:', error);
      let errorMessage = 'خطا در بارگذاری دسته‌بندی‌ها';
      
      if (error?.message) {
        errorMessage = error.message;
      } else if (error?.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error?.code === 'ERR_NETWORK' || !error?.response) {
        errorMessage = 'خطا در اتصال به سرور. لطفاً مطمئن شوید که سرور در حال اجرا است (پورت 8001)';
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      setError('لطفاً نام دسته‌بندی را وارد کنید');
      return;
    }

    setSubmitting(true);
    setError(null);
    
    try {
      // Generate slug from name
      const slug = formData.name
        .toLowerCase()
        .replace(/[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFFa-zA-Z0-9\s]/g, '')
        .replace(/\s+/g, '-')
        .trim();
      
      if (!slug) {
        setError('نام دسته‌بندی باید شامل حروف معتبر باشد');
        setSubmitting(false);
        return;
      }
      
      const categoryData = {
        name: formData.name.trim(),
        slug: slug
      };
      
      if (editingCategory) {
        await updateCategory(editingCategory.id, categoryData);
      } else {
        await createCategory(categoryData);
      }
      
      await loadCategories();
      setShowModal(false);
      setEditingCategory(null);
      setFormData({ name: '' });
      setError(null);
    } catch (error: any) {
      console.error('Error saving category:', error);
      const errorMessage = error?.response?.data?.detail || error?.message || 'خطای نامشخص در ذخیره دسته‌بندی';
      setError(errorMessage);
    } finally {
      setSubmitting(false);
    }
  };

  const handleEdit = (category: Category) => {
    setEditingCategory(category);
    setFormData({ name: category.name });
    setError(null);
    setShowModal(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('آیا مطمئن هستید که می‌خواهید این دسته‌بندی را حذف کنید؟')) {
      return;
    }

    try {
      setError(null);
      await deleteCategory(id);
      await loadCategories();
    } catch (error: any) {
      console.error('Error deleting category:', error);
      const errorMessage = error?.response?.data?.detail || error?.message || 'خطا در حذف دسته‌بندی';
      setError(errorMessage);
      alert('خطا در حذف دسته‌بندی: ' + errorMessage);
    }
  };

  const handleAddNew = () => {
    setEditingCategory(null);
    setFormData({ name: '' });
    setError(null);
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingCategory(null);
    setFormData({ name: '' });
    setError(null);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg">در حال بارگذاری...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">مدیریت دسته‌بندی‌ها</h1>
          <p className="mt-1 text-sm text-gray-600">
            ایجاد و مدیریت دسته‌بندی‌های سوالات
          </p>
        </div>
        <button
          onClick={handleAddNew}
          className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md text-sm font-medium"
        >
          + افزودن دسته‌بندی جدید
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">{error}</p>
              {error.includes('اتصال به سرور') && (
                <p className="text-sm mt-1 text-red-600">
                  لطفاً مطمئن شوید که سرور بک‌اند در حال اجرا است و به آدرس{' '}
                  <code className="bg-red-100 px-1 rounded">http://localhost:8001</code> دسترسی دارد.
                </p>
              )}
            </div>
            <button
              onClick={loadCategories}
              className="ml-4 px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
            >
              تلاش مجدد
            </button>
          </div>
        </div>
      )}

      {/* Categories Grid */}
      {categories.length === 0 && !loading ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-500 text-lg">هیچ دسته‌بندی‌ای وجود ندارد</p>
          <p className="text-gray-400 text-sm mt-2">برای شروع، یک دسته‌بندی جدید اضافه کنید</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {categories.map((category) => (
            <div key={category.id} className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-medium text-gray-900 truncate">
                      {category.name}
                    </h3>
                    {category.slug && (
                      <p className="text-sm text-gray-500 mt-1">Slug: {category.slug}</p>
                    )}
                  </div>
                  <div className="flex items-center space-x-2 space-x-reverse">
                    <button
                      onClick={() => handleEdit(category)}
                      className="text-purple-600 hover:text-purple-900 text-sm font-medium"
                    >
                      ویرایش
                    </button>
                    <button
                      onClick={() => handleDelete(category.id)}
                      className="text-red-600 hover:text-red-900 text-sm font-medium"
                    >
                      حذف
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div 
          className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
          onClick={handleCloseModal}
        >
          <div 
            className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                {editingCategory ? 'ویرایش دسته‌بندی' : 'افزودن دسته‌بندی جدید'}
              </h3>
              {error && (
                <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded-md text-sm">
                  {error}
                </div>
              )}
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    نام دسته‌بندی
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => {
                      setFormData({ ...formData, name: e.target.value });
                      setError(null);
                    }}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm px-3 py-2 focus:ring-purple-500 focus:border-purple-500"
                    required
                    disabled={submitting}
                    autoFocus
                  />
                </div>
                <div className="flex justify-end space-x-3 space-x-reverse">
                  <button
                    type="button"
                    onClick={handleCloseModal}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md disabled:opacity-50"
                    disabled={submitting}
                  >
                    انصراف
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 text-sm font-medium text-white bg-purple-600 hover:bg-purple-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
                    disabled={submitting}
                  >
                    {submitting ? 'در حال ذخیره...' : (editingCategory ? 'ذخیره تغییرات' : 'افزودن دسته‌بندی')}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
