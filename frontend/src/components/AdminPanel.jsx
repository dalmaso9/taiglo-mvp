import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { useAuth } from '../hooks/useAuth';

const API_BASE_URL = 'http://localhost:3000/api';

const AdminPanel = () => {
  const { user, token } = useAuth();
  const [experiences, setExperiences] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  // Estados para formulário de experiência
  const [experienceForm, setExperienceForm] = useState({
    name: '',
    description: '',
    address: '',
    latitude: '',
    longitude: '',
    category_id: '',
    phone: '',
    website_url: '',
    instagram_handle: '',
    price_range: '',
    is_hidden_gem: false
  });

  // Estados para edição
  const [editingExperience, setEditingExperience] = useState(null);
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    if (user && user.role === 'admin') {
      fetchExperiences();
      fetchCategories();
    }
  }, [user]);

  const fetchExperiences = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/experiences?per_page=100`);
      const data = await response.json();
      setExperiences(data.experiences || []);
    } catch (error) {
      setMessage({ type: 'error', text: 'Erro ao carregar experiências' });
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/categories`);
      const data = await response.json();
      setCategories(data.categories || []);
    } catch (error) {
      console.error('Erro ao carregar categorias:', error);
    }
  };

  const handleInputChange = (field, value) => {
    if (isEditing) {
      setEditingExperience(prev => ({ ...prev, [field]: value }));
    } else {
      setExperienceForm(prev => ({ ...prev, [field]: value }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (isEditing) {
      await updateExperience();
    } else {
      await createExperience();
    }
  };

  const createExperience = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/experiences`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(experienceForm)
      });

      const data = await response.json();

      if (response.ok) {
        setMessage({ type: 'success', text: 'Experiência criada com sucesso!' });
        setExperienceForm({
          name: '',
          description: '',
          address: '',
          latitude: '',
          longitude: '',
          category_id: '',
          phone: '',
          website_url: '',
          instagram_handle: '',
          price_range: '',
          is_hidden_gem: false
        });
        fetchExperiences();
      } else {
        setMessage({ type: 'error', text: data.error || 'Erro ao criar experiência' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Erro ao criar experiência' });
    } finally {
      setLoading(false);
    }
  };

  const updateExperience = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/admin/experiences/${editingExperience.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(editingExperience)
      });

      const data = await response.json();

      if (response.ok) {
        setMessage({ type: 'success', text: 'Experiência atualizada com sucesso!' });
        setIsEditing(false);
        setEditingExperience(null);
        fetchExperiences();
      } else {
        setMessage({ type: 'error', text: data.error || 'Erro ao atualizar experiência' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Erro ao atualizar experiência' });
    } finally {
      setLoading(false);
    }
  };

  const deleteExperience = async (id) => {
    if (!confirm('Tem certeza que deseja deletar esta experiência?')) return;

    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/admin/experiences/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setMessage({ type: 'success', text: 'Experiência deletada com sucesso!' });
        fetchExperiences();
      } else {
        const data = await response.json();
        setMessage({ type: 'error', text: data.error || 'Erro ao deletar experiência' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Erro ao deletar experiência' });
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    
    if (!selectedFile) {
      setMessage({ type: 'error', text: 'Selecione um arquivo' });
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('created_by', user.id);

    try {
      setLoading(true);
      setUploadProgress(0);

      const response = await fetch(`${API_BASE_URL}/admin/experiences/bulk-upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      const data = await response.json();

      if (response.ok) {
        setMessage({ 
          type: 'success', 
          text: `Upload concluído! ${data.created_count} experiências criadas.` 
        });
        setSelectedFile(null);
        fetchExperiences();
      } else {
        setMessage({ type: 'error', text: data.error || 'Erro no upload' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Erro no upload' });
    } finally {
      setLoading(false);
      setUploadProgress(0);
    }
  };

  const startEditing = (experience) => {
    setEditingExperience({ ...experience });
    setIsEditing(true);
  };

  const cancelEditing = () => {
    setIsEditing(false);
    setEditingExperience(null);
  };

  const downloadTemplate = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/admin/experiences/template`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      const data = await response.json();
      
      // Criar CSV com os dados do template
      const csvContent = [
        'name,description,address,latitude,longitude,category_id,phone,website_url,instagram_handle,price_range,is_hidden_gem',
        'Restaurante Exemplo,Melhor restaurante da cidade,Rua das Flores 123,-23.5505,-46.6333,1,(11) 99999-9999,https://exemplo.com,@exemplo,2,true'
      ].join('\n');
      
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'template_experiencias.csv';
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      setMessage({ type: 'error', text: 'Erro ao baixar template' });
    }
  };

  if (!user || !user.roles?.some(role => role.name === 'admin')) {
    return (
      <div className="container mx-auto p-6">
        <Alert>
          <AlertDescription>
            Acesso negado. Apenas administradores podem acessar este painel.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Painel de Administração</h1>
        <p className="text-gray-600">Gerencie experiências e conteúdo do sistema</p>
      </div>

      {message.text && (
        <Alert className={`mb-4 ${message.type === 'error' ? 'border-red-500' : 'border-green-500'}`}>
          <AlertDescription className={message.type === 'error' ? 'text-red-700' : 'text-green-700'}>
            {message.text}
          </AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="list" className="space-y-4">
        <TabsList>
          <TabsTrigger value="list">Listar Experiências</TabsTrigger>
          <TabsTrigger value="create">Criar Experiência</TabsTrigger>
          <TabsTrigger value="upload">Upload em Lote</TabsTrigger>
        </TabsList>

        <TabsContent value="list" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Experiências ({experiences.length})</CardTitle>
              <CardDescription>
                Gerencie todas as experiências do sistema
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-4">Carregando...</div>
              ) : (
                <div className="space-y-4">
                  {experiences.map((experience) => (
                    <div key={experience.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <h3 className="font-semibold text-lg">{experience.name}</h3>
                          <p className="text-gray-600 text-sm">{experience.description}</p>
                          <p className="text-gray-500 text-xs mt-1">{experience.address}</p>
                          <div className="flex gap-2 mt-2">
                            {experience.is_hidden_gem && (
                              <Badge variant="secondary">Hidden Gem</Badge>
                            )}
                            {experience.is_verified && (
                              <Badge variant="outline">Verificado</Badge>
                            )}
                            <Badge variant="outline">
                              Rating: {experience.average_rating?.toFixed(1) || 'N/A'}
                            </Badge>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => startEditing(experience)}
                          >
                            Editar
                          </Button>
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => deleteExperience(experience.id)}
                          >
                            Deletar
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="create" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>
                {isEditing ? 'Editar Experiência' : 'Criar Nova Experiência'}
              </CardTitle>
              <CardDescription>
                {isEditing ? 'Modifique os dados da experiência' : 'Adicione uma nova experiência ao sistema'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="name">Nome *</Label>
                    <Input
                      id="name"
                      value={isEditing ? editingExperience?.name : experienceForm.name}
                      onChange={(e) => handleInputChange('name', e.target.value)}
                      required
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="category">Categoria</Label>
                    <Select
                      value={isEditing ? editingExperience?.category_id : experienceForm.category_id}
                      onValueChange={(value) => handleInputChange('category_id', value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione uma categoria" />
                      </SelectTrigger>
                      <SelectContent>
                        {categories.map((category) => (
                          <SelectItem key={category.id} value={category.id}>
                            {category.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div>
                  <Label htmlFor="description">Descrição *</Label>
                  <Textarea
                    id="description"
                    value={isEditing ? editingExperience?.description : experienceForm.description}
                    onChange={(e) => handleInputChange('description', e.target.value)}
                    required
                    rows={3}
                  />
                </div>

                <div>
                  <Label htmlFor="address">Endereço *</Label>
                  <Input
                    id="address"
                    value={isEditing ? editingExperience?.address : experienceForm.address}
                    onChange={(e) => handleInputChange('address', e.target.value)}
                    required
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="latitude">Latitude *</Label>
                    <Input
                      id="latitude"
                      type="number"
                      step="any"
                      value={isEditing ? editingExperience?.latitude : experienceForm.latitude}
                      onChange={(e) => handleInputChange('latitude', e.target.value)}
                      required
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="longitude">Longitude *</Label>
                    <Input
                      id="longitude"
                      type="number"
                      step="any"
                      value={isEditing ? editingExperience?.longitude : experienceForm.longitude}
                      onChange={(e) => handleInputChange('longitude', e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="phone">Telefone</Label>
                    <Input
                      id="phone"
                      value={isEditing ? editingExperience?.phone : experienceForm.phone}
                      onChange={(e) => handleInputChange('phone', e.target.value)}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="website">Website</Label>
                    <Input
                      id="website"
                      type="url"
                      value={isEditing ? editingExperience?.website_url : experienceForm.website_url}
                      onChange={(e) => handleInputChange('website_url', e.target.value)}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="instagram">Instagram</Label>
                    <Input
                      id="instagram"
                      value={isEditing ? editingExperience?.instagram_handle : experienceForm.instagram_handle}
                      onChange={(e) => handleInputChange('instagram_handle', e.target.value)}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="price_range">Faixa de Preço</Label>
                    <Select
                      value={isEditing ? editingExperience?.price_range : experienceForm.price_range}
                      onValueChange={(value) => handleInputChange('price_range', value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione a faixa de preço" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1">Barato (até R$ 30)</SelectItem>
                        <SelectItem value="2">Moderado (R$ 30 - R$ 80)</SelectItem>
                        <SelectItem value="3">Caro (R$ 80 - R$ 150)</SelectItem>
                        <SelectItem value="4">Muito caro (acima de R$ 150)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="is_hidden_gem"
                    checked={isEditing ? editingExperience?.is_hidden_gem : experienceForm.is_hidden_gem}
                    onChange={(e) => handleInputChange('is_hidden_gem', e.target.checked)}
                  />
                  <Label htmlFor="is_hidden_gem">Hidden Gem</Label>
                </div>

                <div className="flex gap-2">
                  <Button type="submit" disabled={loading}>
                    {loading ? 'Salvando...' : (isEditing ? 'Atualizar' : 'Criar')}
                  </Button>
                  {isEditing && (
                    <Button type="button" variant="outline" onClick={cancelEditing}>
                      Cancelar
                    </Button>
                  )}
                </div>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="upload" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Upload em Lote</CardTitle>
              <CardDescription>
                Faça upload de múltiplas experiências via planilha Excel ou CSV
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <Button onClick={downloadTemplate} variant="outline">
                    Baixar Template
                  </Button>
                  <p className="text-sm text-gray-600 mt-2">
                    Baixe o template para ver o formato correto dos dados
                  </p>
                </div>

                <form onSubmit={handleFileUpload} className="space-y-4">
                  <div>
                    <Label htmlFor="file">Arquivo (Excel ou CSV)</Label>
                    <Input
                      id="file"
                      type="file"
                      accept=".xlsx,.xls,.csv"
                      onChange={(e) => setSelectedFile(e.target.files[0])}
                      required
                    />
                  </div>

                  <Button type="submit" disabled={loading || !selectedFile}>
                    {loading ? 'Fazendo Upload...' : 'Fazer Upload'}
                  </Button>
                </form>

                {uploadProgress > 0 && (
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div 
                      className="bg-blue-600 h-2.5 rounded-full" 
                      style={{ width: `${uploadProgress}%` }}
                    ></div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdminPanel;
